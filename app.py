from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize database
from database import init_db

init_db()


# Helper function to get database connection
def get_db():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn


# Routes for Products
@app.route('/')
def index():
    return redirect(url_for('products'))


@app.route('/products', methods=['GET', 'POST'])
def products():
    conn = get_db()

    if request.method == 'POST':
        product_id = request.form['product_id']
        product_name = request.form['product_name']

        try:
            conn.execute('INSERT INTO Product (product_id, product_name) VALUES (?, ?)',
                         (product_id, product_name))
            conn.commit()
            flash('Product added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Product ID already exists!', 'error')

        return redirect(url_for('products'))

    products = conn.execute('SELECT * FROM Product ORDER BY product_id').fetchall()
    conn.close()
    return render_template('products.html', products=products)


@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = get_db()

    if request.method == 'POST':
        product_name = request.form['product_name']

        conn.execute('UPDATE Product SET product_name = ? WHERE product_id = ?',
                     (product_name, product_id))
        conn.commit()
        conn.close()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))

    product = conn.execute('SELECT * FROM Product WHERE product_id = ?', (product_id,)).fetchone()
    conn.close()
    return render_template('edit_product.html', product=product)


@app.route('/delete_product/<product_id>')
def delete_product(product_id):
    conn = get_db()
    conn.execute('DELETE FROM Product WHERE product_id = ?', (product_id,))
    conn.commit()
    conn.close()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products'))


# Routes for Locations
@app.route('/locations', methods=['GET', 'POST'])
def locations():
    conn = get_db()

    if request.method == 'POST':
        location_id = request.form['location_id']
        location_name = request.form['location_name']

        try:
            conn.execute('INSERT INTO Location (location_id, location_name) VALUES (?, ?)',
                         (location_id, location_name))
            conn.commit()
            flash('Location added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Location ID already exists!', 'error')

        return redirect(url_for('locations'))

    locations = conn.execute('SELECT * FROM Location ORDER BY location_id').fetchall()
    conn.close()
    return render_template('locations.html', locations=locations)


@app.route('/edit_location/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    conn = get_db()

    if request.method == 'POST':
        location_name = request.form['location_name']

        conn.execute('UPDATE Location SET location_name = ? WHERE location_id = ?',
                     (location_name, location_id))
        conn.commit()
        conn.close()
        flash('Location updated successfully!', 'success')
        return redirect(url_for('locations'))

    location = conn.execute('SELECT * FROM Location WHERE location_id = ?', (location_id,)).fetchone()
    conn.close()
    return render_template('edit_location.html', location=location)


@app.route('/delete_location/<location_id>')
def delete_location(location_id):
    conn = get_db()
    conn.execute('DELETE FROM Location WHERE location_id = ?', (location_id,))
    conn.commit()
    conn.close()
    flash('Location deleted successfully!', 'success')
    return redirect(url_for('locations'))


# Routes for Product Movements
@app.route('/movements', methods=['GET', 'POST'])
def movements():
    conn = get_db()

    if request.method == 'POST':
        movement_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        from_location = request.form['from_location'] if request.form['from_location'] else None
        to_location = request.form['to_location'] if request.form['to_location'] else None
        product_id = request.form['product_id']
        qty = int(request.form['qty'])

        # Validate that both from and to locations are not the same
        if from_location and to_location and from_location == to_location:
            flash('From and To locations cannot be the same!', 'error')
            return redirect(url_for('movements'))

        # Validate that at least one location is provided
        if not from_location and not to_location:
            flash('At least one location (From or To) must be specified!', 'error')
            return redirect(url_for('movements'))

        try:
            conn.execute('''INSERT INTO ProductMovement
                                (movement_id, timestamp, from_location, to_location, product_id, qty)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                         (movement_id, timestamp, from_location, to_location, product_id, qty))
            conn.commit()
            flash('Product movement recorded successfully!', 'success')
        except Exception as e:
            flash(f'Error recording movement: {str(e)}', 'error')

        return redirect(url_for('movements'))

    movements_data = conn.execute('''
                                  SELECT m.*,
                                         p.product_name,
                                         fl.location_name as from_location_name,
                                         tl.location_name as to_location_name
                                  FROM ProductMovement m
                                           LEFT JOIN Product p ON m.product_id = p.product_id
                                           LEFT JOIN Location fl ON m.from_location = fl.location_id
                                           LEFT JOIN Location tl ON m.to_location = tl.location_id
                                  ORDER BY m.timestamp DESC
                                  ''').fetchall()

    products = conn.execute('SELECT * FROM Product ORDER BY product_id').fetchall()
    locations = conn.execute('SELECT * FROM Location ORDER BY location_id').fetchall()
    conn.close()

    return render_template('movements.html', movements=movements_data,
                           products=products, locations=locations)


@app.route('/edit_movement/<movement_id>', methods=['GET', 'POST'])
def edit_movement(movement_id):
    conn = get_db()

    if request.method == 'POST':
        from_location = request.form['from_location'] if request.form['from_location'] else None
        to_location = request.form['to_location'] if request.form['to_location'] else None
        product_id = request.form['product_id']
        qty = int(request.form['qty'])

        # Validate that both from and to locations are not the same
        if from_location and to_location and from_location == to_location:
            flash('From and To locations cannot be the same!', 'error')
            return redirect(url_for('edit_movement', movement_id=movement_id))

        # Validate that at least one location is provided
        if not from_location and not to_location:
            flash('At least one location (From or To) must be specified!', 'error')
            return redirect(url_for('edit_movement', movement_id=movement_id))

        conn.execute('''UPDATE ProductMovement
                        SET from_location = ?,
                            to_location   = ?,
                            product_id    = ?,
                            qty           = ?
                        WHERE movement_id = ?''',
                     (from_location, to_location, product_id, qty, movement_id))
        conn.commit()
        conn.close()
        flash('Movement updated successfully!', 'success')
        return redirect(url_for('movements'))

    movement = conn.execute('''
                            SELECT m.*,
                                   p.product_name,
                                   fl.location_name as from_location_name,
                                   tl.location_name as to_location_name
                            FROM ProductMovement m
                                     LEFT JOIN Product p ON m.product_id = p.product_id
                                     LEFT JOIN Location fl ON m.from_location = fl.location_id
                                     LEFT JOIN Location tl ON m.to_location = tl.location_id
                            WHERE m.movement_id = ?
                            ''', (movement_id,)).fetchone()

    products = conn.execute('SELECT * FROM Product ORDER BY product_id').fetchall()
    locations = conn.execute('SELECT * FROM Location ORDER BY location_id').fetchall()
    conn.close()

    return render_template('edit_movement.html', movement=movement,
                           products=products, locations=locations)


@app.route('/delete_movement/<movement_id>')
def delete_movement(movement_id):
    conn = get_db()
    conn.execute('DELETE FROM ProductMovement WHERE movement_id = ?', (movement_id,))
    conn.commit()
    conn.close()
    flash('Movement deleted successfully!', 'success')
    return redirect(url_for('movements'))


# Route for Balance Report
@app.route('/balance')
def balance():
    conn = get_db()

    # Calculate balance using SQL query
    balance_data = conn.execute('''
                                WITH movements AS (SELECT product_id,
                                                          to_location as location,
                                                          qty         as positive
                                                   FROM ProductMovement
                                                   WHERE to_location IS NOT NULL

                                                   UNION ALL

                                                   SELECT product_id,
                                                          from_location as location,
                                                          -qty          as positive
                                                   FROM ProductMovement
                                                   WHERE from_location IS NOT NULL)
                                SELECT p.product_id,
                                       p.product_name,
                                       l.location_id,
                                       l.location_name,
                                       COALESCE(SUM(m.positive), 0) as balance
                                FROM Product p
                                         CROSS JOIN Location l
                                         LEFT JOIN movements m
                                                   ON p.product_id = m.product_id AND l.location_id = m.location
                                GROUP BY p.product_id, p.product_name, l.location_id, l.location_name
                                HAVING balance != 0
                                ORDER BY p.product_name, l.location_name
                                ''').fetchall()

    conn.close()
    return render_template('balance.html', balance_data=balance_data)


if __name__ == '__main__':
    app.run(debug=True)
