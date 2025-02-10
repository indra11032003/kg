from flask import Flask, render_template, request, jsonify
from scripts.nlp.coreference import resolve_coreferences
from scripts.nlp.relation_extraction import extract_relationships
from scripts.nlp.summarization import generate_summary
from scripts.nlp.qa import answer_question
from scripts.utils.file_utils import extract_text_from_file
from scripts.utils.neo4j_utils import Neo4jConnector

app = Flask(__name__)

# Initialize Neo4j connector
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Indrajit11"
neo4j_connector = Neo4jConnector(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    graph_data = None
    if request.method == "POST":
        text = request.form.get("text_input")
        file = request.files.get("file_input")

        if file:
            text = extract_text_from_file(file)

        # Coreference resolution
        resolved_text = resolve_coreferences(text)

        # Relationship extraction
        relationships = extract_relationships(resolved_text)

        # Summarization
        summary = generate_summary(resolved_text)

        # Store relationships in Neo4j
        for triplet in relationships:
            subject, relation, obj = triplet.split(", ")
            neo4j_connector.create_node("Entity", {"name": subject})
            neo4j_connector.create_node("Entity", {"name": obj})
            neo4j_connector.create_relationship(
                "Entity", {"name": subject},
                "Entity", {"name": obj},
                relation
            )

        # Fetch graph data for visualization
        graph_data = neo4j_connector.get_graph_data()

    return render_template("index.html", summary=summary, graph_data=graph_data)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")
    context = data.get("context")
    answer = answer_question(question, context)
    return jsonify({"answer": answer})

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    text = data.get("text")
    if not text:
        return jsonify({"summary": "No input text provided."}), 400

    # Generate summary
    summary = generate_summary(text)
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug=True)