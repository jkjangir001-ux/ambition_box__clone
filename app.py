from flask import Flask, render_template, request
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    df = pd.read_csv("all_ambition_data.csv")
    
    if request.method == 'POST':
        location = request.form.get('location')
        industry = request.form.get('industry')
        rating = request.form.get('rating')
        output = request.form.get('output')
        
        # Filter the dataframe
        filtered_df = df.copy()
        
        if location and location != 'Select Location':
            filtered_df = filtered_df[filtered_df['Location'].str.contains(location, na=False)]
        if industry and industry != 'Select Industry':
            filtered_df = filtered_df[filtered_df['Industry'].str.contains(industry, na=False)]
        if rating and rating != 'Select Rating':
            try:
                filtered_df = filtered_df[filtered_df['Rating'] == float(rating)]
            except:
                pass
        
        if output == 'table':
            return render_template("table_page.html", data=filtered_df.to_dict('records'))
        elif output == 'charts':
            print(f"Generating charts for {len(filtered_df)} records")
            # Process data for visualization
            def parse_number(s):
                if pd.isna(s) or s == '--':
                    return 0
                s = str(s).strip()
                if 'k' in s.lower():
                    return float(s.replace('k', '').replace('K', '')) * 1000
                elif 'l' in s.lower():
                    return float(s.replace('l', '').replace('L', '')) * 100000
                else:
                    try:
                        return float(s)
                    except:
                        return 0

            filtered_df['Jobs_parsed'] = filtered_df['Jobs'].apply(parse_number)
            filtered_df['Salery_parsed'] = filtered_df['Salery'].apply(parse_number)
            filtered_df['Review_parsed'] = filtered_df['Review'].apply(parse_number)

            # Create graphs
            if not os.path.exists('static'):
                os.makedirs('static')
                print("Created static directory")

            graphs = []
            
            # Graph 1: Top 10 companies by rating
            try:
                if len(filtered_df) > 0:
                    plt.figure(figsize=(10,6))
                    top10 = filtered_df.nlargest(min(10, len(filtered_df)), 'Rating')
                    if len(top10) > 0:
                        plt.bar(range(len(top10)), top10['Rating'])
                        plt.title('Top Companies by Rating')
                        plt.xticks(range(len(top10)), [str(name)[:15] + '...' if len(str(name)) > 15 else str(name) for name in top10['Company_Names']], rotation=45, ha='right')
                        plt.ylabel('Rating')
                        plt.tight_layout()
                        plt.savefig('static/graph1.png', dpi=100, bbox_inches='tight')
                        plt.close()
                        graphs.append('graph1.png')
                        print("Generated graph1.png")
            except Exception as e:
                print(f"Error generating graph1: {e}")

            # Graph 2: Rating vs Number of Reviews
            try:
                if len(filtered_df) > 0:
                    plt.figure(figsize=(8,6))
                    plt.scatter(filtered_df['Review_parsed'], filtered_df['Rating'], alpha=0.6)
                    plt.title('Rating vs Number of Reviews')
                    plt.xlabel('Number of Reviews')
                    plt.ylabel('Rating')
                    plt.grid(True, alpha=0.3)
                    plt.tight_layout()
                    plt.savefig('static/graph2.png', dpi=100, bbox_inches='tight')
                    plt.close()
                    graphs.append('graph2.png')
                    print("Generated graph2.png")
            except Exception as e:
                print(f"Error generating graph2: {e}")

            # Graph 3: Industry Distribution
            try:
                if len(filtered_df) > 0:
                    plt.figure(figsize=(8,6))
                    industry_counts = filtered_df['Industry'].value_counts()
                    if len(industry_counts) > 0:
                        plt.pie(industry_counts.values, labels=industry_counts.index, autopct='%1.1f%%', startangle=90)
                        plt.title('Industry Distribution')
                        plt.axis('equal')
                        plt.tight_layout()
                        plt.savefig('static/graph3.png', dpi=100, bbox_inches='tight')
                        plt.close()
                        graphs.append('graph3.png')
                        print("Generated graph3.png")
            except Exception as e:
                print(f"Error generating graph3: {e}")

            # Graph 4: Rating Distribution
            try:
                if len(filtered_df) > 0:
                    plt.figure(figsize=(8,6))
                    plt.hist(filtered_df['Rating'], bins=10, alpha=0.7, edgecolor='black')
                    plt.title('Rating Distribution')
                    plt.xlabel('Rating')
                    plt.ylabel('Frequency')
                    plt.grid(True, alpha=0.3)
                    plt.tight_layout()
                    plt.savefig('static/graph4.png', dpi=100, bbox_inches='tight')
                    plt.close()
                    graphs.append('graph4.png')
                    print("Generated graph4.png")
            except Exception as e:
                print(f"Error generating graph4: {e}")

            # Graph 5: Average Rating by Industry
            try:
                if len(filtered_df) > 0:
                    plt.figure(figsize=(10,6))
                    avg_rating = filtered_df.groupby('Industry')['Rating'].mean().reset_index()
                    if len(avg_rating) > 0:
                        plt.bar(range(len(avg_rating)), avg_rating['Rating'])
                        plt.title('Average Rating by Industry')
                        plt.xticks(range(len(avg_rating)), [str(ind)[:15] + '...' if len(str(ind)) > 15 else str(ind) for ind in avg_rating['Industry']], rotation=45, ha='right')
                        plt.ylabel('Average Rating')
                        plt.tight_layout()
                        plt.savefig('static/graph5.png', dpi=100, bbox_inches='tight')
                        plt.close()
                        graphs.append('graph5.png')
                        print("Generated graph5.png")
            except Exception as e:
                print(f"Error generating graph5: {e}")

            # Graph 6: Jobs vs Salary Scatter
            try:
                if len(filtered_df) > 0:
                    plt.figure(figsize=(8,6))
                    plt.scatter(filtered_df['Jobs_parsed'], filtered_df['Salery_parsed'], alpha=0.6)
                    plt.title('Jobs vs Salary')
                    plt.xlabel('Number of Jobs')
                    plt.ylabel('Salary')
                    plt.grid(True, alpha=0.3)
                    plt.tight_layout()
                    plt.savefig('static/graph6.png', dpi=100, bbox_inches='tight')
                    plt.close()
                    graphs.append('graph6.png')
                    print("Generated graph6.png")
            except Exception as e:
                print(f"Error generating graph6: {e}")

            print(f"Generated {len(graphs)} graphs total")
            return render_template("visualization_page.html", graphs=graphs)
    
    # For GET request
    locations = df['Location'].dropna().unique()
    industries = df['Industry'].dropna().unique()
    ratings = sorted(df['Rating'].dropna().unique())
    
    return render_template('home.html', locations=locations, industries=industries, ratings=ratings)

app.run(debug=True, port=5700) 