# Custom WebSearch AI Agent using LangGraph

Welcome to our new Custom WebSearch Agent, now as an easy-to-use Streamlit app! No more sifting through loads of generic results. With this app, you get a search experience that's all about you. It's like having your own personal search assistant right at your fingertips. Just type in what you're looking for, and our app powered by LangGraph gets you exactly what you need. It's super simple to use, and you'll love how it finds stuff that's spot-on for you. So whether you're into specific topics or just curious about new things, our app makes surfing the web a breeze.

## Prerequisites

- [LangGraph](https://python.langchain.com/v0.1/docs/langgraph/) is a library for building stateful, multi-actor applications with LLMs.
  - **StateGraph**: `StateGraph` is a class that represents the graph.
  - **Nodes**: After creating a `StateGraph`, you then add nodes with `graph.add_node(name, value)` syntax.
  - **Edges**: After adding nodes, you can then add edges to create the graph. There are a few types of edges.
    - **The Starting Edge**: This is the edge that connects the start of the graph to a particular node. This will make it so that that node is the first one called when input is passed to the graph.
    - **Normal Edges**: These are edges where one node should ALWAYS be called after another. An example of this may be in the basic agent runtime, where we always want the model to be called after we call a tool.
    - **Conditional Edges**: These are where a function (often powered by an LLM) is used to determine which node to go to first.
  - **Compile**: After we define our graph, we can compile it into a runnable! This simply takes the graph definition we've created so far an returns a runnable.

## Clone and Navigate to the Repository

1. **Clone the Repo:**

   ```bash
   git clone https://github.com/Bhavik-Jikadara/custom-websearch-agent.git
   ```

2. **Navigate to the Repo:**

   ```bash
   cd custom-websearch-agent
   ```

3. **Create a Virtual Environment:**

   ```bash
   pip install virtualenv
   virtualenv venv
   ```

4. **Activate the Virtual Environment:**

   ```bash
   source venv/Scripts/activate
   ```

5. **Install Requirements:**

   ```bash
   pip install -r requirements.txt
   ```

## Configure API Keys

### Step 3: Rename of .env.example filename to .env file and add api keys

- **OpenAI API Key:** Get it from [https://openai.com/](https://openai.com/)
- **Serper API Key:** Get it from [https://serper.dev/](https://serper.dev/)

    ```bash
    OPENAI_API_KEY=""
    SERPER_API_KEY=""
    ```

## Run Your Query

- Now, run project

    ```bash
    python app.py
    ```

## License

The Multiple PDFs QueryBot is released under the [Apache License 2.0](https://github.com/Bhavik-Jikadara/multiple-pdfs-querybot/blob/main/LICENSE).
