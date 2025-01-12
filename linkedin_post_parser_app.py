
import streamlit as st
import pandas as pd
import re

# Parsing functions
def parse_post(clipboard_content):
    lines = [line.strip() for line in clipboard_content.splitlines() if line.strip()]
    author = lines[0] if lines else "Unknown"
    post_title = " ".join(lines[2].split()[:7]) if len(lines) > 2 else "Untitled Post"
    reactions_count = 30  # Simulated for demonstration
    comments_count = 33   # Simulated for demonstration
    return {"Author": author, "Post Title": post_title, "Reactions Count": reactions_count, "Comments Count": comments_count}

def parse_reactions(reactions_content, post_name, post_author):
    reactions = []
    for line in reactions_content:
        line = line.strip()
        if "View" in line and "profile" in line:
            cleaned_name = re.sub(r"View.*profile|[^\w\s,.']", "", line.split("View")[0]).strip()
            reactions.append({"Post Name": post_name, "Post Author": post_author, "Reactor Name": cleaned_name, "Degree": "2nd"})
    return reactions

def parse_comments(comments_content, post_name, post_author):
    comments = []
    unique_commenters = set()
    previous_line = ""
    for line in comments_content:
        line = line.strip()
        if "•" in line and ("1st" in line or "2nd" in line or "Out of network" in line):
            commenter_name = previous_line.strip()
            if commenter_name and commenter_name not in unique_commenters:
                unique_commenters.add(commenter_name)
                comments.append({"Post Name": post_name, "Post Author": post_author, "Commenter Name": commenter_name})
        previous_line = line
    return comments

def combine_parsed_data(post_data, reactions_data, comments_data):
    combined_data = [
        {"Post Name": post_data["Post Title"], "Post Author": post_data["Author"],
         "Reactions Count": post_data["Reactions Count"], "Comments Count": post_data["Comments Count"]}
    ]
    combined_data.extend(reactions_data)
    combined_data.extend(comments_data)
    return pd.DataFrame(combined_data)

# Streamlit UI
st.title("LinkedIn Post Parser Bot")
st.write("Upload your LinkedIn post, reactions, and comments to generate a clean CSV file.")

# Step 1: Post input
post_input = st.text_area("Paste your LinkedIn post content below:", height=200)

# Step 2: Reactions upload
reactions_file = st.file_uploader("Upload reactions.txt file:", type=["txt"])

# Step 3: Comments upload
comments_file = st.file_uploader("Upload comments.txt file:", type=["txt"])

# Process and generate CSV
if st.button("Generate CSV"):
    if not post_input:
        st.error("Please paste your LinkedIn post content.")
    else:
        post_data = parse_post(post_input)

        reactions_data = []
        if reactions_file:
            reactions_content = reactions_file.read().decode("utf-8").splitlines()
            reactions_data = parse_reactions(reactions_content, post_data["Post Title"], post_data["Author"])

        comments_data = []
        if comments_file:
            comments_content = comments_file.read().decode("utf-8").splitlines()
            comments_data = parse_comments(comments_content, post_data["Post Title"], post_data["Author"])

        combined_df = combine_parsed_data(post_data, reactions_data, comments_data)

        # Save CSV and provide download link
        csv_file = "linkedin_parsed_output.csv"
        combined_df.to_csv(csv_file, index=False)
        st.success("CSV file generated successfully!")
        st.download_button("Download CSV", data=open(csv_file, "rb"), file_name="linkedin_parsed_output.csv")
