import aiohttp
import asyncio
import boto3
import json

# Maximum concurrent requests allowed at a time
CONCURRENT_REQUESTS = 10  # Adjust if needed
MAX_RETRIES = 2  # Number of retries for a timeout

# Function to load URLs from a JSON file
def load_urls(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        return data['urls']

# Load the list of URLs from the JSON file
urls = load_urls('urls.json')

# Function to invoke another Lambda function using boto3
def invoke_lambda_function(url, status_code, site_priority):
    lambda_client = boto3.client('lambda', region_name='ap-south-1')  # Set to your specified region
    payload = {
        'type': 'site-check',
        'website': url,
        'statuscode': status_code,
        'sitePriority': site_priority
    }

    try:
        response = lambda_client.invoke(
            FunctionName='testlogs1',
            InvocationType='Event',
            Payload=json.dumps(payload)
        )
        print(f"Invoked Lambda for URL: {url} with Status Code: {status_code}")
    except Exception as e:
        print(f"Failed to invoke Lambda for URL {url}: {str(e)}")

# Function to check URL status and invoke Lambda function for each URL
async def check_url_status(session, url, semaphore):
    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                async with session.get(url, timeout=10) as response:
                    status_code = response.status
                    site_priority = 0  # Set your logic for determining priority here
                    if status_code == 200:
                        print(f"URL {url} is working. Status Code: {status_code}")
                    else:
                        print(f"URL {url} is not working. Status Code: {status_code}")
                        invoke_lambda_function(url, status_code, site_priority)
                    break  # Exit the retry loop on success

            except asyncio.TimeoutError:
                print(f"Request to {url} timed out. Attempt {attempt + 1} of {MAX_RETRIES}.")
                if attempt == MAX_RETRIES - 1:  # If it's the last attempt
                    invoke_lambda_function(url, "Timeout", 0)

            except aiohttp.ClientConnectionError:
                print(f"Failed to connect to {url}.")
                invoke_lambda_function(url, "ConnectionError", 0)
                break  # Don't retry on connection errors

            except Exception as e:
                print(f"An error occurred with {url}: {str(e)}")
                invoke_lambda_function(url, "Error", 0)
                break  # Don't retry on other exceptions

# Main function to run the URL checks concurrently
async def main(urls):
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession() as session:
        tasks = [check_url_status(session, url, semaphore) for url in urls]
        await asyncio.gather(*tasks)

# Lambda handler function
def lambda_handler(event, context):
    asyncio.run(main(urls))
