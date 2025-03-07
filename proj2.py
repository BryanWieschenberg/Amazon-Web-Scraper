import os
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import random

# I put the Selenium executable in my C drive, we can make it run on other devices by putting the matching path
os.environ['PATH'] += r"C:\Selenium"
driver = webdriver.Chrome()
rng = random.randint(1, 3)

def get_amazon_reviews(product_url):
    driver.get(product_url)
    # Gets us to the correct review page
    driver.find_element(By.XPATH, '//*[@id="acrCustomerReviewText"]').click()
    time.sleep(rng)
    driver.find_element(By.CSS_SELECTOR, "[data-hook='see-all-reviews-link-foot']").click()
    time.sleep(rng)
    
    # EXTRACT REVIEWS
    # Finds the users who wrote each review
    profiles = driver.find_elements(By.CSS_SELECTOR, '.a-profile')
    # Finds the star ratings of each review
    stars = driver.find_elements(By.CSS_SELECTOR, '[data-hook="review-star-rating"]')
    rating = []
    for i in stars:
        if "a-star-5" in i.get_attribute('class'):
            rating.append(5)
        elif "a-star-4" in i.get_attribute('class'):
            rating.append(4)
        elif "a-star-3" in i.get_attribute('class'):
            rating.append(3)
        elif "a-star-2" in i.get_attribute('class'):
            rating.append(2)
        else:
            rating.append(1)
    
    hearts = []
    bias = []
    for i in range(10):
        driver.implicitly_wait(1)
        profiles[2+(i*2)].click()
        try:
            elem = driver.find_element(By.CSS_SELECTOR, '.impact-text')
            hearts.append(int(elem.text))
            bias.append(0) # Appended 0 values means the bias values have to be determined after this
        except NoSuchElementException:
            hearts.append(-1) # If the heart value is -1, that means the user is verified, so they get an automatic bias lvl of 1
            bias.append(1)
        driver.execute_script("window.history.go(-1)")
        profiles = driver.find_elements(By.CSS_SELECTOR, '.a-profile')
        time.sleep(rng)
    
    j = 0
    while j < len(profiles):
        if len(profiles[j].text) == 0:
            profiles.pop(j)
        else:
            j += 1
    profiles.pop(0)
    profiles.pop(0)
    reviews = driver.find_elements(By.CSS_SELECTOR, '[data-hook="review-body"]')
    
    # --- ADJUSTED AVG SCORE METHODOLOGY ---
    # If the profiles has <10 hearts, that reviewer has a bias lvl of 3 (high chance they are bias, so we will not account for their score)
    # If the profile has >= 10 and <30 hearts and their product review was <300 characters, that reviewer also has a bias lvl of 3
    # If the profile has >=10 and <30 hearts and their product review was >=300, that reviewer has a bias lvl of 2 (medium chance they are bias, so we will not account for their score)
    # If the profile has >=30 hearts or has a verified badge, that reviewer has a bias lvl of 1 (best chance they are not bias, so we will only account for their score for the most accurate adjusted score)
    # For the adjusted average score, We will only find the average of the scores from profiles with the lowest bias lvl, of 1
    
    # Checks for bias, so we'll go through each profile and scan it
    for i in range(len(reviews)):
        if hearts[i] != -1:
            if hearts[i] < 10:
                bias[i] = 3
            if hearts[i] >= 10 and hearts[i] < 30 and len(reviews[i].text) < 300:
                bias[i] = 3
            if hearts[i] >= 10 and hearts[i] < 30 and len(reviews[i].text) >= 300:
                bias[i] = 2
            if hearts[i] >= 30:
                bias[i] = 1

    # Prints every profile name, hearts, rating, bias, and review text
    for i in range(len(reviews)):
        print(profiles[i].text + " (", end='')
        if hearts[i] > 0:
            print(str(hearts[i]) + " hearts", end='')
        else:
            print("Verified User", end='')
        print(") - " + str(rating[i]) + "/5 stars - Bias lvl " + str(bias[i]) + " - \"" + str(reviews[i].text[:50]) + "\"...")
    print()

    # Calculates unadjusted and adjusted average scores of the reviews
    avgUnadjusted = 0.00
    scoreAdjusted = 0.00
    scoreAdjustedTotal = 0.00
    for i in range(len(reviews)):
        avgUnadjusted += rating[i]
        if bias[i] == 1:
            scoreAdjusted += rating[i]
            scoreAdjustedTotal += 5
    avgUnadjusted /= len(reviews)
    scoreAdjusted /= scoreAdjustedTotal
    scoreAdjusted *= 5

    print("Unadjusted average score of the reviews (just taking ratings into account): " + str(round(avgUnadjusted, 3)) + "/5 stars")
    print("Adjusted average score of the reviews (taking user bias into account): " + str(round(scoreAdjusted, 3)) + "/5 stars")

if __name__ == "__main__":
    product_url = 'https://www.amazon.com/Bose-QuietComfort-Cancelling-Headphones-Bluetooth/dp/B0CCZ26B5V/ref=sr_1_2_sspa?keywords=bose%2Bquietcomfort&qid=1699901267&sr=8-2-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1'
    get_amazon_reviews(product_url)

driver.quit()
