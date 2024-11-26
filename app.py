import csv
from flask import Flask, request, send_file, render_template
from jobspy import scrape_jobs

app = Flask(__name__)


@app.route("/")
def home():
    # Serve the HTML form
    return render_template(
        "index.html"
    )  # Ensure your HTML is saved as 'templates/index.html'


@app.route("/search", methods=["POST"])
def search():
    # Get form data
    search_term = request.form.get("job")
    location = request.form.get("location")
    sites = request.form.getlist("sites")  # Checkboxes send lists

    # Perform the job scraping
    jobs = scrape_jobs(
        site_name=sites,
        search_term=search_term,
        google_search_term=f"{search_term} jobs near {location}",
        location=location,
        results_wanted=20,
        hours_old=72,  # Adjust as needed
        country_indeed="USA",  # Example, adjust for your needs
    )

    # Save jobs to a CSV file
    output_file = "jobs.csv"
    jobs.to_csv(output_file, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)

    # Return the CSV file for download
    return send_file(
        output_file,
        as_attachment=True,
        download_name="jobs.csv",
        mimetype="text/csv"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
