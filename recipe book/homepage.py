import json
from flask import Flask
from flask import render_template, request
import csv
import pandas as pd
import re

app = Flask(__name__)
datadict = {}
ingredient_list = []
data_pd = pd.read_csv("static/Data.csv")
meal_col = data_pd["Meal"]
cusine_col = data_pd["Cuisine"]
prep_col = data_pd["Prep Time"]
# ingredient_list = [row.split(",") for row in ingredient_col]
# ingredient_list = set(x.strip() for l in ingredient_list for x in l)

with open("static/Data.csv", 'r+', encoding="utf-8") as f:
    data = csv.DictReader(f)
    for row in data:
        name = row['Name']
        ingredients = row['Ingredients']
        for i in ingredients.split(","):
            i = i.strip()
            if i not in ingredient_list:
                ingredient_list.append(i)
        ingredient_list.sort()
        recipe = re.findall(r'\d.*',row['Recipe'])
        prep = row['Prep Time']
        fullName = row['Full Name']
        datadict[name] = (ingredients, recipe, prep, fullName)

meals = {i:[] for i in meal_col.unique()}
cuisines = {i: [] for i in cusine_col.unique()}
times = {i: [] for i in prep_col.unique()}
for item in datadict:
    item_row = data_pd.loc[data_pd['Name'] == item]
    name = item_row['Name'].item()
    meals[item_row['Meal'].item()].append(name)
    cuisines[item_row['Cuisine'].item()].append(name)
    times[item_row['Prep Time'].item()].append(name)


appetizers = data_pd.loc[data_pd["Meal"] == "appetizer"]["Name"].tolist()
entrees = data_pd.loc[data_pd["Meal"] == "entrée"]["Name"].tolist()
desserts = data_pd.loc[data_pd["Meal"] == "dessert"]["Name"].tolist()
drinks = data_pd.loc[data_pd["Meal"] == "drink"]["Name"].tolist()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ingredients', methods=["GET","POST"])
def ingredients():
    if request.method == 'POST':
        result = request.form.getlist('ingredients')
        select = set()
        for item in datadict:
            for x in result:
                chosen = [i.strip() for i in datadict[item][0].split(',')]
                if x in chosen:
                    select.add(item)

        return render_template('ingredients.html', 
            ilist = ingredient_list, 
            data = datadict, 
            selected = True,
            selected_list = result,
            filters = [("Results", select)],
        )
    return render_template('ingredients.html', ilist = ingredient_list, data = datadict, selected=False)

@app.route('/meal-builder', methods=["GET", "POST"])
def meal_builder():
    presets = {
        "american":["quinoa", "mexican-pizza", "oreo-truffles", "mojito"],
        "italian":["quinoa", "ravioli", "cake", "mojito"],
        "mexican":["quinoa", "spinach-puffs", "chocchipcookies", "mojito"]
    }

    builder = {
        "appetizer": appetizers,
        "entree": entrees,
        "dessert": desserts,
        "drink": drinks
    }

    if request.method == 'POST':
        result = request.form.get('change')
        if result in presets.keys():
            preset = presets[result]
            appetizers.remove(preset[0])
            appetizers.insert(0, preset[0])
            entrees.remove(preset[1])
            entrees.insert(0, preset[1])
            desserts.remove(preset[2])
            desserts.insert(0, preset[2])
            drinks.remove(preset[3])
            drinks.insert(0, preset[3])
        else:
            col = builder[result]
            first = col[0]
            col.remove(col[0])
            col.append(first)

        return render_template('meal-builder.html', 
            data = datadict,
            appetizers = appetizers,
            entrees = entrees,
            desserts = desserts,
            drinks = drinks
        )

    else:
        return render_template('meal-builder.html', 
            data=datadict,
            appetizers = appetizers,
            entrees = entrees,
            desserts = desserts,
            drinks = drinks
        )

@app.route('/recipes')
@app.route('/recipes-time')
def recipes_time():
    my_order = ["breakfast", "appetizer","entrée", "dessert", "drink"]
    order = {key: i for i, key in enumerate(my_order)}
    my_filters = sorted([(k,meals[k]) for k in meals], key=lambda d:order[d[0]])
    return render_template('recipes.html', 
        data = datadict,
    	filters = my_filters
    )

@app.route('/recipes-cuisine')
def recipes_cuisine():
    my_filters = [(k,cuisines[k]) for k in cuisines]
    return render_template('recipes.html',
        data = datadict, 
    	filters = my_filters
    )

@app.route('/recipes-prep')
def recipes_prep():
    my_order = ["10-20 min", "20-30 min", "30-40 min", "50-60 min", "1-2 hrs"]
    order = {key: i for i, key in enumerate(my_order)}
    my_filters = sorted([(k,times[k]) for k in times], key=lambda d:order[d[0]])
    return render_template('recipes.html', 
        data = datadict,
        filters = my_filters
    )

@app.route('/search', methods=["GET", "POST"])
def search():
    if request.method == 'POST':
        result = request.form.get('search')
        data = data_pd.loc[data_pd["Full Name"].str.lower().str.contains(result.lower(), regex=False)]
        name = data['Name']
        print("count: ", name.shape[0])
        if name.shape[0] == 1:
            return render_template('search.html',
                data = data,
                datadict = datadict[name.item()],
                item = result
            )
        else:
            return render_template('search-plural.html',
                data = data,
                names = name.tolist(),
                datadict = '',
                item = result
            )

@app.route('/aboutus')
def about():
    return render_template('aboutus.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)

