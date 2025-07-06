from flask import Flask, render_template, request, redirect
import psycopg2
from db import insert_estimate, get_all_estimates  # existing imports

app = Flask(__name__)

# --- Material Rates ---
material_rates = {
    'brick': 14.5,
    'cement': 1385,
    'steel': 242,
    'sand': 33.5
}

# --- Material Estimates by Plot Size ---
material_estimates = {
    "120": { 'bricks': 45000, 'cement': 500, 'steel': 3000, 'sand': 1500 },
    "200": { 'bricks': 75000, 'cement': 800, 'steel': 5000, 'sand': 2500 },
    "500": { 'bricks': 180000, 'cement': 1800, 'steel': 12000, 'sand': 6000 }
}

# PostgreSQL DB connection
conn = psycopg2.connect(
    dbname="construction",       # ✅ change if needed
    user="postgres",             # ✅ change if needed
    password="54321",            # ✅ change if needed
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# --- Static Pages ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('service.html')

@app.route('/contractor')
def contractor():
    return render_template('contractor.html')

@app.route('/material')
def material():
    return render_template('material.html')

@app.route('/projects')
def projects():
    return render_template('project.html')

@app.route('/features')
def features():
    return render_template('feature.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

@app.route('/404')
def page404():
    return render_template('404.html')

@app.route('/contact')
def contact():
    print("Contact route hit ✅")
    return render_template('contact.html')

# --- Submit Hiring Form ---
@app.route('/submit_request', methods=['POST'])
def submit_request():
    description = request.form['project_description']
    budget = request.form['budget']
    start_date = request.form['start_date']
    contact_info = request.form['contact_info']
    contractor_name = request.form['contractor_name']  # Naya field

    cursor.execute("""
        INSERT INTO hire_requests (project_description, budget, start_date, contact_info, contractor_name)
        VALUES (%s, %s, %s, %s, %s)
    """, (description, budget, start_date, contact_info, contractor_name))
    conn.commit()

    success_message = "Hire a contractor successfully!"
    return render_template('contractor.html', success_message=success_message)



# --- Estimator ---
@app.route('/estimator', methods=['GET', 'POST'])
def estimator():
    if request.method == 'POST':
        plot_size = request.form['plotSize']
        floors = int(request.form['floors'])

        estimate = material_estimates[plot_size]
        bricks = estimate['bricks'] * floors
        cement = estimate['cement'] * floors
        steel = estimate['steel'] * floors
        sand = estimate['sand'] * floors

        cost_brick = int(bricks * material_rates['brick'])
        cost_cement = int(cement * material_rates['cement'])
        cost_steel = int(steel * material_rates['steel'])
        cost_sand = int(sand * material_rates['sand'])
        total = cost_brick + cost_cement + cost_steel + cost_sand

        insert_estimate({
            'plot_size': plot_size,
            'floors': floors,
            'bricks': bricks,
            'cement': cement,
            'steel': steel,
            'sand': sand,
            'cost_brick': cost_brick,
            'cost_cement': cost_cement,
            'cost_steel': cost_steel,
            'cost_sand': cost_sand,
            'total': total
        })

        result = {
            'plot_size': plot_size,
            'floors': floors,
            'bricks': f"{bricks:,}",
            'cement': cement,
            'steel': steel,
            'sand': sand,
            'rates': material_rates,
            'costs': {
                'brick': f"{cost_brick:,}",
                'cement': f"{cost_cement:,}",
                'steel': f"{cost_steel:,}",
                'sand': f"{cost_sand:,}"
            },
            'total': f"{total:,}"
        }

        return render_template('indexxx.html', result=result)

    return render_template('indexxx.html', result=None)

# --- Estimation History ---
@app.route('/history')
def history():
    estimates = get_all_estimates()
    return render_template('history.html', estimates=estimates)


if __name__ == '__main__':
    app.run(debug=True)
