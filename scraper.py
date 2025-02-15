import requests
from bs4 import BeautifulSoup
import pymongo
import numpy as np

# Function to scrape job listings from Indeed
def scrape_jobs():
    url = "https://www.indeed.com/jobs?q=Python+Developer&l="  # Update URL if needed
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Unable to fetch page (Status Code {response.status_code})")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    job_cards = soup.find_all('div', class_='job_seen_beacon')  # Update selector if needed

    jobs = []
    for job in job_cards:
        title_elem = job.find('h2')
        company_elem = job.find('span', class_='companyName')
        location_elem = job.find('div', class_='companyLocation')
        salary_elem = job.find('div', class_='salary-snippet')

        if title_elem and company_elem and location_elem:
            jobs.append({
                "title": title_elem.text.strip(),
                "company": company_elem.text.strip(),
                "location": location_elem.text.strip(),
                "salary": salary_elem.text.strip() if salary_elem else "Not Provided"
            })

    print(f"Scraped {len(jobs)} jobs")  # Debugging statement
    return jobs

# Function to save data to MongoDB
def save_to_mongodb(jobs):
    if not jobs:  # Check if list is empty
        print("No jobs found. Skipping database insertion.")
        return

    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["job_scraper"]
    collection = db["jobs"]

    collection.insert_many(jobs)
    print("Jobs inserted into MongoDB successfully!")

# Function to calculate average salary
def calculate_average_salary(jobs):
    salaries = []

    for job in jobs:
        salary_text = job["salary"]
        if salary_text != "Not Provided":
            try:
                salary_numbers = [int(s.replace("$", "").replace(",", "")) for s in salary_text.split() if s.replace("$", "").replace(",", "").isdigit()]
                if salary_numbers:
                    avg_salary = sum(salary_numbers) / len(salary_numbers)
                    salaries.append(avg_salary)
            except ValueError:
                continue

    if salaries:
        avg_salary = np.mean(salaries)
        print(f"Average Salary: ${avg_salary:.2f}")
    else:
        print("No salary data available.")

# Main execution
if __name__ == "__main__":
    jobs = scrape_jobs()
    save_to_mongodb(jobs)
    calculate_average_salary(jobs)
