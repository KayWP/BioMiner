import streamlit as st
import pandas as pd
import os

def main():
    st.set_page_config(page_title="DataFrame Review Tool",
                       layout="wide")
    
    # Initialize session state
    if 'current_df_index' not in st.session_state:
        st.session_state.current_df_index = 0
        st.session_state.dfs = set_up_df()
        st.session_state.completed = [False] * len(st.session_state.dfs)
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Previous") and st.session_state.current_df_index > 0:
            st.session_state.current_df_index -= 1
            st.rerun()
    
    with col2:
        st.write(f"DataFrame {st.session_state.current_df_index + 1} of {len(st.session_state.dfs)}")
        # Show progress indicators
        progress_text = ""
        for i, completed in enumerate(st.session_state.completed):
            if i == st.session_state.current_df_index:
                progress_text += "🔵 "  # Current
            elif completed:
                progress_text += "✅ "  # Completed
            else:
                progress_text += "⭕ "  # Not completed
        st.write(progress_text)
    
    with col3:
        # Only show standalone Next button if current DataFrame is already saved
        if (st.session_state.completed[st.session_state.current_df_index] and 
            st.button("Next →") and 
            st.session_state.current_df_index < len(st.session_state.dfs) - 1):
            st.session_state.current_df_index += 1
            st.rerun()
    
    # Review current DataFrame
    review_and_save(st.session_state.current_df_index)

def set_up_df():
    dataframes = []
    folder_path = "generated_frames"
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            dataframes.append(df)
    if not dataframes:
        raise FileNotFoundError("No CSV files found in 'generated_frames'.")
    return dataframes

def review_and_save(df_index):
    df = st.session_state.dfs[df_index]
    
    st.title(f"Review DataFrame {df_index + 1}")
    
    # Show completion status
    if st.session_state.completed[df_index]:
        st.success("✅ This DataFrame has been saved!")
    
    # Editable dataframe
    edited_df = st.data_editor(df, use_container_width=True)
    
    # Update the stored DataFrame
    st.session_state.dfs[df_index] = edited_df
    
    # Combined Save & Next button logic
    is_last_df = df_index == len(st.session_state.dfs) - 1
    is_already_saved = st.session_state.completed[df_index]
    
    # Button text changes based on context
    if is_last_df:
        button_text = "Save & Finish" if not is_already_saved else "Update & Finish"
    else:
        button_text = "Save & Next →" if not is_already_saved else "Update & Next →"
    
    # Combined button
    if st.button(button_text, type="primary"):
        # Save the current DataFrame
        header = df_index == 0 and not any(st.session_state.completed[:df_index])  # Header only for first unsaved DF
        edited_df.to_csv('output.csv', mode='a', header=header, index=False)
        st.session_state.completed[df_index] = True
        
        if is_last_df:
            # Last DataFrame - show completion message
            st.success("🎉 All DataFrames saved successfully! Review complete.")
            st.balloons()
            
            # Show summary
            with st.expander("📊 Summary"):
                st.write(f"✅ Processed {len(st.session_state.dfs)} DataFrames")
                st.write(f"📁 Saved to: output.csv")
                total_rows = sum(len(df) for df in st.session_state.dfs)
                st.write(f"📈 Total rows saved: {total_rows}")
        else:
            # Not last DataFrame - save and move to next
            st.success("Data saved successfully!")
            st.session_state.current_df_index += 1
            st.rerun()
    
    # Optional: Show a summary of all DataFrames at the bottom
    if st.session_state.current_df_index == len(st.session_state.dfs) - 1:
        with st.expander("📋 Review Summary"):
            for i, completed in enumerate(st.session_state.completed):
                status = "✅ Saved" if completed else "⏳ Pending"
                st.write(f"DataFrame {i + 1}: {status}")

if __name__ == "__main__":
    main()