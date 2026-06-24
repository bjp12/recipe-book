import json
from flask import Flask
from flask import render_template, request
import re

app = Flask(__name__)
datadict = {}
ingredient_lookup = {}

with open("static/Data.json") as f:
    data = json.load(f)

    meal_col = {row["Meal"] for row in data}
    cuisine_col = {row["Cuisine"] for row in data}
    prep_col = {row["Prep Time"] for row in data}

    meals = {i: [] for i in meal_col}
    cuisines = {i: [] for i in cuisine_col}
    times = {i: [] for i in prep_col}

    ingredient_set = set()
    
    for row in data:
        name = row['Name']

        ingredients = {
            ingredient.strip()
            for ingredient in row["Ingredients"].split(",")
        }

        ingredient_lookup[name] = ingredients
        ingredient_set.update(ingredients)
        
        meals[row["Meal"]].append(name)
        cuisines[row["Cuisine"]].append(name)
        times[row["Prep Time"]].append(name)
        
        recipe = re.findall(r'\d.*',row['Recipe'])
        datadict[name] = (
            row["Ingredients"], 
            recipe, 
            row["Prep Time"], 
            row["Full Name"]
        )
    ingredient_list = sorted(ingredient_set)

appetizers = meals.get("appetizer", [])
entrees = meals.get("entrée", [])
desserts = meals.get("dessert", [])
drinks = meals.get("drink", [])

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
                if x in ingredient_lookup[item]:
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
        
        matches = [
            row for row in data
            if result.lower() in row["Full Name"].lower()
        ]
        if len(matches) == 0:
            return render_template(
                'search-plural.html',
                data=[],
                names=[],
                datadict='',
                item=result
            )
        elif len(matches) == 1:
            match = matches[0]
        
            return render_template(
                'search.html',
                data=match,
                datadict=datadict[match["Name"]],
                item=result
            )
        else: 
            names = [row["Name"] for row in matches]
            return render_template(
                'search-plural.html',
                data = matches,
                names = names,
                datadict = '',
                item = result
            )

@app.route('/aboutus')
def about():
    return render_template('aboutus.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=False)

