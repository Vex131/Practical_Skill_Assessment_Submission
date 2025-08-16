from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from mysql.connector import Error
from datetime import date
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret_key"


def get_db_connection():
    """Return a new connection using the session config."""
    db_config = session.get("db_config")
    if not db_config:
        raise Exception("⚠ No database configuration found. Please connect first.")
    return mysql.connector.connect(**db_config)


# -----------------------------
# Routes
# -----------------------------

# Home Page
@app.route("/", methods=["GET", "POST"])
def home():

    # Use defaults to pre-fill form
    db_config = session.get("db_config", {
        "host": "localhost",
        "user": "root",
        "password": "9949460",
        "database": "asset_management"
    })

    if request.method == "POST":
        # Get form values
        db_config = {
            "host": request.form.get("host"),
            "user": request.form.get("user"),
            "password": request.form.get("password"),
            "database": request.form.get("database")
        }

        # Test connection
        try:
            conn = mysql.connector.connect(**db_config)
            conn.close()
            flash("✅ Database connected successfully!", "success")

            # Save config into session
            session["db_config"] = db_config
            session["db_connected"] = True

        except Exception as e:
            if e.errno == 1045:
                flash("❌ Connection failed: Wrong username or password!", "danger")
            elif e.errno == 1049:
                flash(f"❌ Connection failed: Unknown database '{db_config['database']}'", "danger")
            elif e.errno == 2005:
                flash(f"❌ Connection failed: Unknown MySQL server host '{db_config['host']}'", "danger")
            else:
                flash(f"❌ Connection failed: {e}", "danger")

            # on failure, clear session
            session.pop("db_config", None)
            session["db_connected"] = False

    return render_template("home.html", db_config=db_config, db_connected=session.get("db_connected"))


@app.route("/disconnect")
def disconnect():
    session.pop("db_config", None)
    session["db_connected"] = False
    flash("🔌 Disconnected from database.", "info")
    return redirect(url_for("home"))


# Staff Page
@app.route("/staff")
def staff_page():
    if "db_config" not in session or not session.get("db_connected"):
        flash("⚠ You must connect to the database first!", "warning")
        return redirect(url_for("home"))

    staff_id = request.args.get("staff_id", type=int)
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Fetch staff list for dropdown
    cursor.execute("SELECT * FROM Staff ORDER BY name")
    staff_list = cursor.fetchall()

    selected_staff = None
    current_assets = []
    history = []

    if staff_id:
        # Selected staff info
        cursor.execute("SELECT * FROM Staff WHERE staffNumber = %s", (staff_id,))
        selected_staff = cursor.fetchone()

        # Current assets
        cursor.execute("""
            SELECT a.assetNumber, a.assetType, ah.assignedDate
            FROM AssetHistory ah
            JOIN Asset a ON ah.assetNumber = a.assetNumber
            WHERE ah.staffNumber = %s AND ah.returnedDate IS NULL
        """, (staff_id,))
        current_assets = cursor.fetchall()

        # Assignment history
        cursor.execute("""
            SELECT a.assetNumber, a.assetType, ah.assignedDate, ah.returnedDate
            FROM AssetHistory ah
            JOIN Asset a ON ah.assetNumber = a.assetNumber
            WHERE ah.staffNumber = %s
            ORDER BY ah.assignedDate DESC
        """, (staff_id,))
        history = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("staff.html",
                           staff_list=staff_list,
                           selected_staff=selected_staff,
                           current_assets=current_assets,
                           history=history)


# Add Asset
@app.route("/add_asset", methods=["GET", "POST"])
def add_asset():
    if request.method == "POST":
        asset_type = request.form.get("asset_type")
        purchased_date = request.form.get("purchased_date")
        status = request.form.get("status")

        if asset_type and purchased_date and status:
            try:
                db = get_db_connection()
                cursor = db.cursor()
                cursor.execute("""
                    INSERT INTO Asset (assetType, status, purchasedDate)
                    VALUES (%s, %s, %s)
                """, (asset_type, status, purchased_date))
                db.commit()
                cursor.close()
                db.close()
                # Redirect to the list of assets after successful addition
                return redirect(url_for('list_assets'))
            except Exception as e:
                message = f"❌ Error: {e}"
                cursor.close()
                db.close()
                return render_template("add_asset.html", message=message)
        else:
            message = "❌ Please fill all fields."
            return render_template("add_asset.html", message=message)

    # GET request
    return render_template("add_asset.html", message="")


# Assign Asset
@app.route("/assign_asset/<int:asset_id>", methods=["GET", "POST"])
def assign_asset(asset_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Get asset details
    cursor.execute("SELECT * FROM Asset WHERE assetNumber = %s", (asset_id,))
    asset = cursor.fetchone()

    if not asset:
        cursor.close()
        db.close()
        return "Asset not found", 404

    if request.method == "POST":
        staff_number = request.form["staff_number"]

        # Validation
        if asset["status"] == "Assigned":
            message = "❌ Asset is already assigned!"
        elif asset["status"] == "Discarded":
            message = "❌ Cannot assign a discarded asset!"
        else:
            today = date.today()

            # Get staff department for location update
            cursor.execute("SELECT department FROM Staff WHERE staffNumber = %s", (staff_number,))
            staff = cursor.fetchone()
            location = staff["department"] if staff else "In Storage"

            # Insert into AssetHistory with returnedDate NULL
            cursor.execute("""
                INSERT INTO AssetHistory (assetNumber, staffNumber, assignedDate, returnedDate)
                VALUES (%s, %s, %s, NULL)
            """, (asset_id, staff_number, today))

            # Update asset table
            cursor.execute("""
                UPDATE Asset 
                SET status = 'Assigned', location = %s
                WHERE assetNumber = %s
            """, (location, asset_id))

            db.commit()
            cursor.close()
            db.close()
            return redirect("/assets")

        # If validation failed
        cursor.execute("SELECT staffNumber, name FROM Staff")
        staff_list = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template("assign_asset.html", asset=asset, staff_list=staff_list, message=message)

    # GET request → load staff list
    cursor.execute("SELECT staffNumber, name FROM Staff")
    staff_list = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("assign_asset.html", asset=asset, staff_list=staff_list)


# Return Asset
@app.route("/return_asset/<int:asset_number>", methods=["POST"])
def return_asset(asset_number):
    db = get_db_connection()
    cursor = db.cursor()

    # Update the returned date in AssetHistory
    cursor.execute("""
        UPDATE AssetHistory
        SET returnedDate = %s
        WHERE assetNumber = %s AND returnedDate IS NULL
    """, (date.today(), asset_number))

    # Update the Asset status to "Not Assigned"
    cursor.execute("""
        UPDATE Asset
        SET status = 'Not Assigned'
        WHERE assetNumber = %s
    """, (asset_number,))

    db.commit()
    cursor.close()
    db.close()

    flash(f"Asset #{asset_number} has been returned successfully.", "success")
    return redirect(url_for("list_assets"))


# Edit Asset
@app.route("/edit_asset/<int:asset_id>", methods=["GET", "POST"])
def edit_asset(asset_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Fetch the asset info
    cursor.execute("SELECT * FROM Asset WHERE assetNumber = %s", (asset_id,))
    asset = cursor.fetchone()

    if request.method == "POST":
        asset_type = request.form.get("asset_type")
        status = request.form.get("status")
        purchased_date = request.form.get("purchased_date")
        discarded_date = request.form.get("discarded_date") or None

        # Prevent changing status if currently Assigned
        if asset["status"] == "Assigned" and status != "Assigned":
            message = "❌ Cannot change the status of an assigned asset."
            cursor.close()
            db.close()
            return render_template("edit_asset.html", asset=asset, message=message)

        # If asset is discarded, set location to NULL
        new_location = None if status == "Discarded" else asset["location"]

        try:
            cursor.execute("""
                UPDATE Asset
                SET assetType=%s, status=%s, purchasedDate=%s, discardedDate=%s, location=%s
                WHERE assetNumber=%s
            """, (asset_type, status, purchased_date, discarded_date, new_location, asset_id))
            db.commit()
            cursor.close()
            db.close()
            return redirect(url_for('list_assets'))
        except Exception as e:
            message = f"❌ Error: {e}"
            cursor.close()
            db.close()
            return render_template("edit_asset.html", asset=asset, message=message)

    cursor.close()
    db.close()
    return render_template("edit_asset.html", asset=asset)


# List All Assets
@app.route("/assets")
def list_assets():
    if "db_config" not in session or not session.get("db_connected"):
        flash("⚠ You must connect to the database first!", "warning")
        return redirect(url_for("home"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            a.assetNumber, 
            a.assetType, 
            a.status, 
            a.purchasedDate, 
            a.discardedDate,
            CASE WHEN ah.returnedDate IS NULL AND a.status='Assigned' THEN ah.staffNumber ELSE NULL END AS staffNumber,
            CASE WHEN ah.returnedDate IS NULL AND a.status='Assigned' THEN s.name ELSE NULL END AS staffName,
            CASE 
                WHEN a.status = 'Discarded' THEN NULL
                WHEN a.status = 'Not Assigned' THEN 'In Storage'
                ELSE a.location
            END AS location,
            CASE WHEN ah.returnedDate IS NULL AND a.status='Assigned' THEN ah.assignedDate ELSE NULL END AS assignedDate,
            ah.returnedDate
        FROM Asset a
        LEFT JOIN AssetHistory ah
            ON ah.assignmentId = (
                SELECT assignmentId 
                FROM AssetHistory
                WHERE assetNumber = a.assetNumber
                ORDER BY assignedDate DESC
                LIMIT 1
            )
        LEFT JOIN Staff s ON ah.staffNumber = s.staffNumber
        ORDER BY a.assetNumber;
    """)
    assets = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("list_assets.html", assets=assets)

# Route for staff details
@app.route("/api/staff/<int:staff_id>")
def api_staff_details(staff_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Staff info
    cursor.execute("SELECT * FROM Staff WHERE staffNumber = %s", (staff_id,))
    staff = cursor.fetchone()

    # Current assignments
    cursor.execute("""
        SELECT a.assetNumber, a.assetType, ah.assignedDate
        FROM AssetHistory ah
        JOIN Asset a ON ah.assetNumber = a.assetNumber
        WHERE ah.staffNumber = %s AND ah.returnedDate IS NULL
    """, (staff_id,))
    current_assets = cursor.fetchall()

    # Assignment history
    cursor.execute("""
        SELECT a.assetNumber, a.assetType, ah.assignedDate, ah.returnedDate
        FROM AssetHistory ah
        JOIN Asset a ON ah.assetNumber = a.assetNumber
        WHERE ah.staffNumber = %s
        ORDER BY ah.assignedDate DESC
    """, (staff_id,))
    history = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify({
        "staff": staff,
        "current_assets": current_assets,
        "history": history
    })