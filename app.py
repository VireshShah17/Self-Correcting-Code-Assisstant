import streamlit as st
from agent import run_agent

# --- UI Configuration ---
st.set_page_config(page_title = "Agentic Code Assistant", page_icon = "🤖", layout = "wide")
st.title("🤖 AI Code Assistant")
st.markdown("An autonomous AI agent that writes, tests, and fixes its own Python code.")

# --- Main App UI ---
user_task = st.text_area(
    "👨‍💻 What would you like the AI to build?", 
    height = 100, 
    placeholder = "e.g., Write a function that calculates the factorial of a number and include assert statements to test it..."
)

if st.button("🚀 Generate & Run", type = "primary"):
    if not user_task:
        st.warning("Please enter a task first!")
    else:
        # We use st.status to show a live expanding container of what the agent is doing
        with st.status("Initializing Agent...", expanded = True) as status_box:
            
            # Consume the yielded states from the backend generator
            for step in run_agent(user_task):
                
                # Update the spinner label and print the step based on the current action
                if step["status"] in ["generating", "validating", "executing", "installing"]:
                    status_box.update(label = step["message"])
                    st.write(step["message"])
                
                elif step["status"] == "code_generated":
                    st.markdown("### Generated Code:")
                    st.code(step["code"], language = "python")
                    
                elif step["status"] == "security_error":
                    st.error(f"🚫 SECURITY BLOCK: {step['error']}")
                    
                elif step["status"] == "install_success":
                    st.info(step["message"])
                    
                elif step["status"] == "install_error":
                    st.error(step["error"])
                    
                elif step["status"] == "execution_error":
                    st.error(f"❌ Code Execution Failed:\n```text\n{step['error']}\n```")
                    
                elif step["status"] == "success":
                    st.success("✅ Code executed successfully!")
                    st.markdown("### Output:")
                    st.code(step["output"], language = "text")
                    status_box.update(label = "Task Complete!", state = "complete")

                elif step["status"] == "fatal_error":
                    st.error(step["message"])
                    status_box.update(label = "Task Failed.", state = "error")