import pandas as pd
import os
import requests
import sys
import matplotlib.pyplot as plt
import numpy as np


def pie_chart(df):
    # Step 1: Recode countries with fewer than 25 laureates as 'Other countries'
    country_counts = df['born_in'].value_counts()
    countries_to_recod = country_counts[country_counts < 25].index
    df['born_in_recoded'] = df['born_in'].apply(lambda x: 'Other countries' if x in countries_to_recod else x)

    # Step 2: Plot the pie chart
    colors = ['blue', 'orange', 'red', 'yellow', 'green', 'pink', 'brown', 'cyan', 'purple']
    explode = [0.08 if country == 'USA' else 0 for country in df['born_in_recoded'].unique()]

    plt.figure(figsize=(12, 12))
    plt.pie(df['born_in_recoded'].value_counts(), labels=df['born_in_recoded'].value_counts().index, colors=colors,
            autopct=lambda pct: ' {:.2f}%\n({:.0f})'.format(pct, pct / 100 * sum(df['born_in_recoded'].value_counts())),
            startangle=140, explode=explode)
    plt.title('Nobel Laureates Countries of Origin')
    plt.show()

def bar_plot(df):
    df.dropna(subset=['category'], inplace=True)
    df = df[df['category'] != '']
    plt.figure(figsize=(10, 10))
    bar_width = 0.4
    bar_centers = range(len(df['category'].unique()))
    unique_categories = df['category'].unique()
    print(unique_categories)
    for gender in df['gender'].unique():
        gender_data = df[df['gender'] == gender]
        gender_counts = gender_data['category'].value_counts().reindex(unique_categories, fill_value=0)
        plt.bar([center + bar_width / 2 if gender == 'female' else center - bar_width / 2 for center in bar_centers],
                gender_counts.sort_index(), width=bar_width, label='Females' if gender == 'female' else 'Males', color='crimson' if gender == 'female' else 'blue',
                alpha=0.7)  # Adjust alpha for better visibility
    plt.xlabel('Category', fontsize=14)
    plt.ylabel('Nobel Laureates Count', fontsize=14)
    plt.title('The total count of male and female Nobel Prize winners by categories', fontsize=20)
    plt.xticks(bar_centers, unique_categories, rotation=45, fontsize=14)

    # Add legend without handles and labels
    plt.rc('font', size=20)  # Set default font size
    plt.rc('axes', labelsize=14)

    # Show the plot
    plt.show()


def box_plot(df):
    df.dropna(subset=['category'], inplace=True)
    df = df[df['category'] != '']

    plt.figure(figsize=(10, 10))

    lst = []
    labels = []
    for cat in df['category'].unique():
        cat_data = df[df['category'] == cat]
        cat_values = cat_data['age_of_winning'].tolist()  # Get the individual age values
        cat_mean = cat_data['age_of_winning'].mean()
        lst.append(cat_values)
        labels.append(f'{cat}')

    # Exclude non-numeric columns from the mean calculation
    all_categories_mean = df['age_of_winning'].mean()
    lst.append(all_categories_mean)
    labels.append('All categories')

    plt.boxplot(lst, labels=labels, showmeans=True, meanprops={'markerfacecolor':'green'})
    plt.xlabel('Category', fontsize=14)
    plt.ylabel('Age of Obtaining the Nobel Prize', fontsize=14)

    plt.title('Distribution of Ages by Category', fontsize=20)
    plt.show()



if __name__ == '__main__':
    if not os.path.exists('../Data'):
        os.mkdir('../Data')

    # Download data if it is unavailable.
    if 'Nobel_laureates.json' not in os.listdir('../Data'):
        sys.stderr.write("[INFO] Dataset is loading.\n")
        url = "https://www.dropbox.com/s/m6ld4vaq2sz3ovd/nobel_laureates.json?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/Nobel_laureates.json', 'wb').write(r.content)
        sys.stderr.write("[INFO] Loaded.\n")

    # write your code here
    df = pd.read_json('../Data/Nobel_laureates.json')


    df.dropna(inplace=True, subset=['gender'])
    df.reset_index(inplace=True, drop=True)

    # Step 1: Extract country names from 'place_of_birth' column
    df['country'] = df['place_of_birth'].apply(
        lambda x: x.split(',')[-1].strip() if isinstance(x, str) and ',' in x else None)

    # Step 2: Replace empty strings in 'born_in' with NaN
    df['born_in'] = df['born_in'].replace('', pd.NA)

    # Step 3: Fill missing values in 'born_in' column with values from 'place_of_birth'
    df['born_in'] = df.apply(lambda row: row['country'] if pd.isna(row['born_in']) else row['born_in'], axis=1)

    # Step 4: Drop rows where 'born_in' column is still empty
    df = df.dropna(subset=['born_in'])

    # Step 5: Reset the DataFrame index
    df.reset_index(drop=True, inplace=True)

    # Step 6: Modify country names
    df['born_in'] = df['born_in'].replace({'US': 'USA', 'United States': 'USA', 'U.S.': 'USA', 'United Kingdom': 'UK'})

    # Step 7: Output the list of 'born_in' column values
    born_in_values = df['born_in'].tolist()


    # Step 1: Convert the 'date_of_birth' column to a consistent format (year)
    def extract_birth_year(born):
        try:
            # Try to parse the year from the given formats
            return pd.to_datetime(born, errors='coerce').year
        except ValueError:
            return None


    df['year_born'] = df['date_of_birth'].apply(extract_birth_year)

    # Step 2: Create a new column representing the age of winning the prize
    df['age_of_winning'] = df['year'] - df['year_born']

    # Step 3: Output the lists
    birth_year_values = df['year_born'].to_list()
    age_at_prize_values = df['age_of_winning'].to_list()

    # Step 4: Print the result
    result = f"{birth_year_values}\n{age_at_prize_values}"
    box_plot(df)
