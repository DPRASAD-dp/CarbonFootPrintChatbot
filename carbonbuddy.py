import streamlit as st
from faissibm import initialize_system, process_question

def main():
    st.title("CarbonBuddy: Carbon Footprint QA System")
    
    # Automated initialization
    if 'system_initialized' not in st.session_state:
        with st.spinner("Initializing CarbonBuddy..."):
            success, message = initialize_system()
            if success:
                st.session_state['system_initialized'] = True
                st.success(message)
            else:
                st.error(message)
                st.stop()  # Stop the app if initialization fails

    # Main chat interface
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about carbon emissions or the report"):
        st.session_state['messages'].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = process_question(prompt)
                    st.markdown(response)
                    st.session_state['messages'].append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.error("Please try rephrasing your question or try again later.")

if __name__ == "__main__":
    main()