import csv
import os

from flask import Flask, jsonify, render_template, request, send_file
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
    num_queries = int(request.form.get("num_queries", 20))  # Default to 20 if not set
    remote_only = request.form.get("remote-only") == "on"  # Check if checkbox is ticked
    if remote_only and search_term:
        search_term += "remote"

    # Perform the job scraping
    jobs = scrape_jobs(
        site_name=sites,
        search_term=search_term,
        google_search_term=f"{search_term} jobs near {location}",
        location=location,
        results_wanted=num_queries,
        hours_old=72,  # Adjust as needed
        country_indeed="USA",  # Example, adjust for your needs
        remote_only=remote_only,  # Pass this filter if the job scraper supports it
    )

    # Save jobs to a CSV file
    output_file = "jobs.csv"
    jobs.to_csv(output_file, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)

    # Return the CSV file for download
    return send_file(
        output_file, as_attachment=True, download_name="jobs.csv", mimetype="text/csv"
    )


@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json(force=True)  # parse JSON body

    # Inputs analogous to your HTML form
    search_term = data.get("job", "")
    location = data.get("location", "")
    sites = data.get("sites", [])  # list of site names
    num_queries = int(data.get("num_queries", 20))
    remote_only = bool(data.get("remote_only", False))

    if remote_only and search_term:
        search_term = f"{search_term} remote"

    # Run the scraper (same params as your HTML route)
    jobs = scrape_jobs(
        site_name=sites,
        search_term=search_term,
        google_search_term=f"{search_term} jobs near {location}",
        location=location,
        results_wanted=num_queries,
        hours_old=72,
        country_indeed="USA",
        remote_only=remote_only,
    )

    # Clean NaN → None so JSON is nice
    jobs_clean = jobs.where(jobs.notnull(), None)

    # Option A: just return results
    return jsonify(jobs_clean.to_dict(orient="records"))


if __name__ == "__main__":
    port_string = os.getenv("PORT")
    if port_string:
        port = int(port_string)
    else:
        port = 8080
    app.run(host="0.0.0.0", port=port)
