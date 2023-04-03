from flask import Flask, request, Markup, render_template, flash

import os
import json

app = Flask(__name__)

@app.route("/")
def render_home():
    return render_template("home.html")
    
@app.route("/average-sat")
def render_averagesat():
    with open('school_scores.json') as sat_data:
        avgsat = json.load(sat_data)
    if 'state' and 'year' in request.args:
        state = request.args['state']
        year = int(request.args['year'])
        gpa = request.args['gpa']
        if gpa == 'No Selection' or gpa == "No response":
            math = get_score(avgsat, year, state, "Math")
            verb = get_score(avgsat, year, state, "Verbal")
            total = math + verb
        else:
            math = get_gpa_score(avgsat, year, state, gpa, "Math")
            verb = get_gpa_score(avgsat, year, state, gpa, "Verbal")
            if math == "N/A" and verb == "N/A":
                total = "N/A"
            else:
                total = math + verb
        
        return render_template('avgsatdisplay.html', options1 = get_state_options(avgsat), options2 = get_year_options(avgsat), 
        options3 = get_gpa_options(avgsat), math = math, verb = verb, total = total, state = state, year = year, gpa = gpa) 
    return render_template('average_sat.html', options1 = get_state_options(avgsat), options2 = get_year_options(avgsat), 
    options3 = get_gpa_options(avgsat))  
    
@app.route("/sat-demo")
def render_demo():
    with open('school_scores.json') as sat_data:
        avgsat = json.load(sat_data)
    
    if 'state' in request.args:
        choice = request.args['choice']
        state = request.args['state']
        year = int(request.args['year'])
        if choice == "overtime":
            return render_template("demo-graph.html", options1 = get_state_options(avgsat), options2 = get_year_options(avgsat), 
            mathpoints = get_demo_data(state, "Math"), verbpoints = get_demo_data(state, "Verbal"), state = state)
        elif choice == "range":
            return render_template("score-graph.html", options1 = get_state_options(avgsat), options2 = get_year_options(avgsat),
            percents = get_range_data(avgsat, state, year, get_ranges(avgsat)), state = state, year = year)
        else: 
            return render_template("country-graph.html", options1 = get_state_options(avgsat), options2 = get_year_options(avgsat),
            data = get_country_data(avgsat, year, get_states(avgsat)), year = year)
    return render_template("demographics.html", options1 = get_state_options(avgsat), options2 = get_year_options(avgsat))
    
@app.route("/sat-gender")
def render_gender():
    with open('school_scores.json') as sat_data:
        avgsat = json.load(sat_data)
        
    if 'state' and 'year' in request.args:
        state = request.args['state']
        year = int(request.args['year'])
        return render_template("gender-graph.html", options1 = get_state_options(avgsat), options2 = get_year_options(avgsat),
        fmath = get_gender_data(avgsat, state, year, "Female", "Math"), bmath = get_gender_data(avgsat, state, year, "Male", "Math"), 
        fverb = get_gender_data(avgsat, state, year, "Female", "Verbal"), bverb = get_gender_data(avgsat, state, year, "Male", "Verbal"), 
        state = state, year = year)
    return render_template("gender.html", options1 = get_state_options(avgsat), options2 = get_year_options(avgsat),)
  
def get_gender_data(avgsat, state, year, gender, section):
    score = 0
    for a in avgsat:
        if a["Year"] == year and a["State"]["Name"] == state:
            score = a["Gender"][gender][section]
    return score

def get_country_data(data, year, states):
    scores = {}

    for d in data:
        for s in states:
            if s == d["State"]["Name"]:
                total = d["Total"]["Math"] + d["Total"]["Verbal"]
                if d["Year"] == year:
                    if total in scores:
                        scores[s] = scores[s] + total
                    else: 
                        scores[s] = total

    maxim = scores["Alabama"]
    minim = scores["Alabama"]

    for s in scores:
        if scores[s] > maxim:
            maxim = scores[s]
        if scores[s] < minim:
            minim = scores[s]

    code = "["
    for states, score in scores.items():        
        #{ y: 300878, label: "Venezuela" }
        if score == maxim:
            code = code + Markup("{ y: " + str(score) + ", label: '" + states + "', indexLabel: '\u2605 Highest'  },")
        elif score == minim:
            code = code + Markup("{ y: " + str(score) + ", label: '" + states + "', indexLabel: '\u2691 Lowest'  },")
        else:
            code = code + Markup("{ y: " + str(score) + ", label: '" + states + "' },")
    code = code[:-1]
    code = code + "]"
    return code
        
def get_range_data(data, state, year, ranges):
    percentages = {}
    scores = []
    p = 0
    scoresum = 0
    
    for d in data:
        for r in ranges:
            total = d["Score Ranges"][r]["Math"]["Total"] + d["Score Ranges"][r]["Verbal"]["Total"]
            if d["State"]["Name"] == state and d["Year"] == year:
                if total not in scores:
                    scores.append(total)
                if total in percentages:
                    percentages[r] = percentages[r] + total
                else:
                    percentages[r] = total
    
    for num in scores:
        scoresum = scoresum + num
    
    for p in percentages:
        percent = (percentages[p]/scoresum) * 100
        percent_round = round(percent, 1)
        percentages[p] = percent_round
    
    code = "["
    for ranges, percent in percentages.items():        
        #{ y: 20, name: "Medical Aid" }
        code = code + Markup("{ y: " + str(percent) + ", name: '" + str(ranges) + "' },")
    code = code[:-1]
    code = code + "]"
    return code
    
def get_demo_data(state, section):
    with open('school_scores.json') as sat_data:
        avgsat = json.load(sat_data)
    avgsc = {}
    for a in avgsat:
        avg = a["Total"][section]
        if a["State"]["Name"] == state:
            if a["Year"] in avgsc:
                avgsc[a["Year"]] = avgsc[a["Year"]] + avg
            else:
                avgsc[a["Year"]] = avg
    code = "["
    for year, score in avgsc.items():
        code = code + Markup("{ x: " + str(year) + ", y: " + str(score) + " },")
    code = code[:-1]
    code = code + "]"
    return code

def get_score(data, year, state, section):
    score = 0
    for s in data:
        if s["Year"] == year and s["State"]["Name"] == state:
            score = s["Total"][section]
    return score
    
def get_gpa_score(data, year, state, gpa, section):
    score = 0
    for s in data:
        if s["Year"] == year and s["State"]["Name"] == state:
            score = s["GPA"][gpa][section]
            if score == 0:
                score = "N/A"
    return score

def get_states(data):
    states = []
    options = ""
    for d in data:
        state = d["State"]["Name"]
        if (state not in states):
            states.append(state)
    states.sort()
    return states

def get_state_options(data):    
    states = []
    options = ""
    for d in data:
        state = d["State"]["Name"]
        if (state not in states):
            states.append(state)
    states.sort()
    for s in states:
        options += Markup("<option value=\"" + s + "\">" + s + "</option>")
    return options
    
def get_year_options(data):    
    years = []
    options = ""
    for d in data:
        year = d["Year"]
        if (year not in years):
            years.append(year)
            options += Markup("<option value=\"" + str(year) + "\">" + str(year) + "</option>")
    return options

def get_gpa_options(data):
    options = ""
    gpa = data[0]["GPA"]
    for g in gpa:
        options += Markup("<option value=\"" + g + "\">" + g + "</option>")
    return options

def get_ranges(data):
    rangelist = []
    ranges = data[0]["Score Ranges"]
    for r in ranges:
        rangelist.append(r)
    return rangelist

if __name__=="__main__":
    app.run(debug=True)