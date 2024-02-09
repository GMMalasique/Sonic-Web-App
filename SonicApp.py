import lasio
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import tempfile
import missingno as ms
import lascheck
import traceback
from PIL import Image
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title = "Sonic Log Web App",
    layout='wide'
    )

selected_menu = option_menu(
    #menu_title = "None", #required
    None,
    options = ["Home", "About", "User's Guide", "Additional Info", "Interpretation"], #required
    icons = ["house", "patch-question", "journal-bookmark", "lightbulb", "calculator"], #optional
    default_index = 0, #optional
    orientation = "horizontal",
    styles = {
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"}, 
        "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "green"},
        }
    )

if selected_menu == "Home":
    st.title('''Sonic Log Interpretation: Porosity Derivation''')
    st.markdown('''
               Welcome to our Sonic Log Interpretation web application!
               \nThis tool simplifies the process of understanding and extracting valuable insights from well logging data, 
               specifically focusing on porosity derivation.
               With this application, you can effortlessly upload LAS files, visualize log data, and perform formation evaluations. 
               Whether you're a geoscientist, engineer, or anyone working with well data, our user-friendly interface 
               and powerful features make interpreting sonic logs a breeze.
               \nStart exploring your well data today and gain a deeper understanding of subsurface formations.
                ''')

if selected_menu == "About":
    img_about = Image.open("About_us.jpg")    
    st.image(img_about)

if selected_menu == "User's Guide":
    st.subheader("How to Use the Web Application")

if selected_menu == "Additional Info":    
    st.subheader('Porosity Calculation and Evaluation')


# Display the image in Streamlit
    img_wyllie = Image.open("Sonic_Formula.png")
    img_wyllie = img_wyllie.resize([int(img_wyllie.width/3), int(img_wyllie.height/3.5)])
    st.image(img_wyllie, caption= 'Figure 1. Wyllie time average equation')
    
    
    st.markdown('''The Wyllie time average method is used for estimating porosity from sonic measurements. 
                It requires the following input parameters:
             \nϕs = Sonic Porosity
             \nΔtl = Sonic log interval transit time. Typically, its unit is μsec/ft
             \nΔtp = Pore fluid interval transit time.
             \nΔtma = Rock matrix interval transit time    
                 ''')
    
    img_transit = Image.open("Transit_Time.png")
    img_transit = img_transit.resize([int(img_transit.width/3), int(img_transit.height/3.5)])
    st.image(img_transit, caption= 'Figure 2. Typical interval transit time for lithologies and fluids')
    st.divider()
    
    st.subheader('Uncompacted Formation and Hydrocarbon-bearing Zone')
    st.markdown('''The existing equation tends to produce higher porosity estimates when applied to uncompacted sandstones 
                and hydrocarbon-bearing reservoirs. 
                To mitigate this issue, we can introduce empirical corrections using two terms: the compaction factor (Cp) 
                and the hydrocarbon correction (Hy).
                \nCp quantifies the impact of pore pressure on the sonic porosity equation. 
                Typically, it is determined through a comparison of density and apparent sonic porosity or by 
                analyzing the sonic response in nearby shale (Cp = Δtsh/100.0).
                \nHy, on the other hand, is an approximate correction factor and is assigned a value of 0.9 for oil and 0.7 for gas reservoirs.
                \nWith these adjustments, the revised Wyllie time average equation is as follows:''')
    img_correction = Image.open("Correction.png")
    img_correction = img_correction.resize([int(img_correction.width/3), int(img_correction.height/3.5)])
    st.image(img_correction, caption= 'Figure 3. Wyllie time average equation with correction')
    st.markdown('''Cp = Compaction correction factor
                \nHy = Hydrocarbon correction factor  ''')
    st.divider()
    
    st.subheader("Common Log Curve Abbreviations")
    
    st.markdown('''These are common mnemonics and names for log curves that you may encounter in well logging data. 
                Please note that the availability of these curves and their names can vary depending on the specific well logging tools 
                and data acquisition methods used during the logging operation. 
                Always refer to the specific LAS file's "Curve Information" section or documentation to determine the mnemonics 
                and descriptions of the log curves recorded in that file.
                   ''')
    file_url = "https://www.spwla.org/documents/spwla/Mnemonic/reevesmnemonics.pdf"  # Replace with the actual URL of your PDF file
    st.markdown(f'<a href="{file_url}" download="document.pdf">Click here to download complete tools and curve mnemonics.</a>', unsafe_allow_html=True)

    # path_pdf_abbvr = r"C:\Users\Malasique\Documents\GitHub\Sonic-Log-Interpreter-Web-Application\reeves_mnemonics.pdf"
    # st.markdown(f'<a href = {path_pdf_abbvr} download="document.pdf">Click here to download complete tools and curve mnemonics.</a>', unsafe_allow_html=True)           
    img_abbrv = Image.open("Curves_Abbrv.png")
    img_abbrv = img_abbrv.resize([int(img_abbrv.width/1.5), int(img_abbrv.height/1.5)])
    st.image(img_abbrv, caption= 'Figure 4. List of common log curve abbreviations (mnemonics) and their corresponding names or descriptions' )

    
if selected_menu == "Interpretation":
    
    # Function to set interval transit values in μsec/m
    def unit_meter():
        global dt_matrix_sandstone
        global dt_matrix_limestone
        global dt_matrix_dolomite
        global dt_fluid_seawater
        global dt_fluid_freshwater
        global correction_oil
        global correction_gas
        
        dt_matrix_sandstone = 55.5 * 12 * 2.54 * 0.01
        dt_matrix_limestone = 47.5 * 12 * 2.54 * 0.01
        dt_matrix_dolomite = 43.5 * 12 * 2.54 * 0.01
        dt_fluid_seawater = 189 * 12 * 2.54 * 0.01
        dt_fluid_freshwater = 204 * 12 * 2.54 * 0.01
        correction_oil = 0.9
        correction_gas = 0.7

    # Function to set interval transit values in μsec/ft
    def unit_feet():
        global dt_matrix_sandstone
        global dt_matrix_limestone
        global dt_matrix_dolomite
        global dt_fluid_seawater
        global dt_fluid_freshwater
        global correction_oil
        global correction_gas
        
        dt_matrix_sandstone = 55.5
        dt_matrix_limestone = 47.5
        dt_matrix_dolomite = 43.5
        dt_fluid_seawater = 189
        dt_fluid_freshwater = 204
        correction_oil = 0.9
        correction_gas = 0.7
    
    def create_option_menu():
        return option_menu(
            None,
            options=["Las File Specification", "Well Information", "Curve Information", "Curve Data Overview", "Log Visualization"],
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                #"icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "green"},
            }
        ) 
    
    def las_file_specification():
        st.subheader("LAS File Conformity Check Result:")
        try:
            if tfile is None:
                las = lascheck.read(file)
            else:
                las = lascheck.read(tfile.name)  # Use the path of the temporary file
    
            st.text("Checking LAS file conformity...")
    
            # Initialize the progress bar
            progress_bar = st.progress(0)
            progress_status = st.empty()
    
            # Simulate progress by updating the progress bar
            for percent_complete in range(0, 101):
                progress_bar.progress(percent_complete)
                progress_status.text(f"Checking progress: {percent_complete}%")
    
            # Once the checking is complete, display the results
            st.write("LAS file conformity check complete.")
            if las.check_conformity() == True:
                st.write('**Result:** No non-conformities were found in the LAS file.')
            if las.check_conformity() == False:
                st.write('**Result:** Non-conformities were found in the LAS file.')
                st.write(las.get_non_conformities())
    
        except ValueError as ve:
            # Handle the specific error gracefully
            st.warning(f"An error occurred while processing the LAS file: {ve}")
            # Capture and display the traceback
            st.write("Traceback:")
            st.code(traceback.format_exc())
    
        except Exception as e:
            # Handle the exception gracefully
            st.warning(f"An error occurred while processing the LAS file: {e}")
            # Capture and display the traceback
            st.write("Traceback:")
            st.code(traceback.format_exc())
    
        st.warning('**Note**: "-999.25" is the standard value for a Null value ')
        st.divider()    

    def display_well_information():
        st.subheader('Well Information')
        st.markdown(f'Well Name : {well_name}')
        st.markdown(f'Start Depth : {start_depth}')
        st.markdown(f'Stop Depth : {stop_depth}')
        st.markdown(f'Step : {step}')
        st.markdown(f'Company : {company_name}')
        st.markdown(f'Logging Date : {date}')
        st.divider()
    
    def display_curve_information():
        st.subheader('Curve Information')
        st.text(f'================================================\n{curvename}')
        st.divider()
    
    def display_curve_data_overview():
        st.subheader('Curve Data Overview')
        st.markdown('''The value on the left figure is the number of rows. White space in each column of the curve is a missing value row/data. 
                        Expand to see more details''')
        st.pyplot(ms.matrix(las_df, sparkline=False, labels=100).figure)
        st.divider()
    
    st.set_option('deprecation.showfileUploaderEncoding', False)
    tfile = None
    file = None
    selected_tab = None
    
    mode = st.radio(
        "**Select an option:**",
        ('Upload LAS file', 'Use sample LAS file')
    )
    st.divider()
    
    
    if mode == 'Upload LAS file':
        file = st.file_uploader('Upload the LAS file')
        if file is not None:
            # Create a temporary file and save the uploaded file's content into it
            with tempfile.NamedTemporaryFile(delete=False) as tfile:
                tfile.write(file.read())
                las_file = lasio.read(tfile.name)
                las_df = las_file.df()
            
    
    if mode == 'Use sample LAS file':
        file = r"Sample.las"
        las_file = lasio.read(file)
        las_df = las_file.df()
        
        
    if file:
      selected_tab = create_option_menu()
      las_df.insert(0, 'DEPTH', las_df.index)
      las_df.reset_index(drop=True, inplace=True)
    
      try:
        well_name =  las_file.header['Well'].WELL.value
        start_depth = las_df['DEPTH'].min()
        stop_depth = las_df['DEPTH'].max()
        step = abs(las_file.header['Well'].STEP.value)
        company_name =  las_file.header['Well'].COMP.value
        date =  las_file.header['Well'].DATE.value
        curvename = las_file.curves
      except:
        well_name =  'unknown'
        start_depth = 0.00
        stop_depth = 10000.00
        step = abs(las_df['DEPTH'][1]-las_df['DEPTH'][0])
        company_name =  'unknown'
        date =  'unknown'
        curvename = las_file.curves
    
        
    if selected_tab == "Las File Specification":
        las_file_specification()
        
    if selected_tab == "Well Information":
        display_well_information()
    
    if selected_tab == "Curve Information":
        display_curve_information()
      
    if selected_tab == "Curve Data Overview":
        display_curve_data_overview()
    
    if selected_tab == "Log Visualization":   
        selected_column = st.sidebar.selectbox("**Select curve data to visualize:**", las_df.keys())
          
        try:
              unit_curve = las_file.curves[selected_column].unit  # Get unit from the selected curve
              if unit_curve.upper() not in ('US/M', 'US/FT', 'US/F'):
                  st.warning('**Warning**: Unit must be either (us/m) or (us/ft). Assuming the selected curve data is Sonic and its unit is us/ft.')
        except KeyError:
              if selected_column == "DEPTH":
                  unit_curve = las_file.curves[las_file.curves.keys()[0]].unit   # Get unit from the selected curve
              else:
                  unit_curve = "Unknown"
        
        st.sidebar.write(f"Unit of {selected_column} curve: {unit_curve}")
            
        # Determine which unit to use based on unit_curve
        if unit_curve.upper() == 'US/M':
            unit_meter()
        elif unit_curve.upper() == 'US/FT' or 'US/F': 
            unit_feet()
        else:
            st.warning('**Warning**: Unit must be either (us/m) or (us/ft). Assuming the selected curve data is Sonic and its unit is us/ft')
            unit_feet()
        
        st.sidebar.subheader('Sonic Porosity:')
        if file:
            mode_sandstone_seawater = st.sidebar.checkbox("Matrix: Sandstone | Fluid: Seawater")
            mode_limestone_seawater = st.sidebar.checkbox("Matrix: Limestone | Fluid: Seawater")
            mode_dolomite_seawater = st.sidebar.checkbox("Matrix: Dolomite | Fluid: Seawater")
            mode_sandstone_freshwater = st.sidebar.checkbox("Matrix: Sandstone | Fluid: Freshwater") 
            mode_limestone_freshwater = st.sidebar.checkbox("Matrix: Limestone | Fluid: Freshwater")
            mode_dolomite_freshwater = st.sidebar.checkbox("Matrix: Dolomite | Fluid: Freshwater")
            mode_average = st.sidebar.checkbox("Average")
        
        mode = st.sidebar.radio(
              "Hydrocarbon Correction:",
              ('None', 'Oil Correction', 'Gas Correction'))
            
        # Check if 'DT' is a valid curve in the LAS file
        data = []
        temporary = []
        if selected_column in las_file.keys():
            for depth, dt_log in zip(las_df['DEPTH'], las_df[selected_column]):
                # Always include depth and Sonic Log Reading
                row_data = {"Depth": depth, 'Sonic Log Reading': dt_log}
                  
                if mode == 'None':
                    
                    if mode_sandstone_seawater:
                        phi_sandstone_seawater = (dt_log - dt_matrix_sandstone) / (dt_fluid_seawater - dt_matrix_sandstone)
                        row_data['Sonic_Sandstone_Seawater'] = phi_sandstone_seawater
    
                    if mode_limestone_seawater:
                        phi_limestone_seawater = (dt_log - dt_matrix_limestone) / (dt_fluid_seawater - dt_matrix_limestone)
                        row_data['Sonic_Limestone_Seawater'] = phi_limestone_seawater
                    
                    if mode_dolomite_seawater:
                        phi_dolomite_seawater = (dt_log - dt_matrix_dolomite) / (dt_fluid_seawater - dt_matrix_dolomite)
                        row_data['Sonic_Dolomite_Seawater'] = phi_dolomite_seawater
                    
                    if mode_sandstone_freshwater:
                        phi_sandstone_freshwater = (dt_log - dt_matrix_sandstone) / (dt_fluid_freshwater - dt_matrix_sandstone)
                        row_data['Sonic_Sandstone_Freshwater'] = phi_sandstone_freshwater
                    
                    if mode_limestone_freshwater:
                        phi_limestone_freshwater = (dt_log - dt_matrix_limestone) / (dt_fluid_freshwater - dt_matrix_limestone)
                        row_data['Sonic_Limestone_Freshwater'] = phi_limestone_freshwater
                    
                    if mode_dolomite_freshwater:
                        phi_dolomite_freshwater = (dt_log - dt_matrix_dolomite) / (dt_fluid_freshwater - dt_matrix_dolomite)
                        row_data['Sonic_Dolomite_Freshwater'] = phi_dolomite_freshwater
                        
                    # Add similar conditions for other checkboxes (e.g., mode_limestone_freshwater, mode_dolomite_freshwater, etc.)  
                    data.append(row_data)      
                
                if mode == 'Oil Correction':
                    
                    if mode_sandstone_seawater:
                        phi_sandstone_seawater = (dt_log - dt_matrix_sandstone) / (dt_fluid_seawater - dt_matrix_sandstone)
                        row_data['Sonic_Sandstone_Seawater'] = phi_sandstone_seawater * correction_oil
                    
                    if mode_limestone_seawater:
                        phi_limestone_seawater = (dt_log - dt_matrix_limestone) / (dt_fluid_seawater - dt_matrix_limestone)
                        row_data['Sonic_Limestone_Seawater'] = phi_limestone_seawater * correction_oil
                    
                    if mode_dolomite_seawater:
                        phi_dolomite_seawater = (dt_log - dt_matrix_dolomite) / (dt_fluid_seawater - dt_matrix_dolomite)
                        row_data['Sonic_Dolomite_Seawater'] = phi_dolomite_seawater * correction_oil
                    
                    if mode_sandstone_freshwater:
                        phi_sandstone_freshwater = (dt_log - dt_matrix_sandstone) / (dt_fluid_freshwater - dt_matrix_sandstone)
                        row_data['Sonic_Sandstone_Freshwater'] = phi_sandstone_freshwater * correction_oil
                    
                    if mode_limestone_freshwater:
                        phi_limestone_freshwater = (dt_log - dt_matrix_limestone) / (dt_fluid_freshwater - dt_matrix_limestone)
                        row_data['Sonic_Limestone_Freshwater'] = phi_limestone_freshwater * correction_oil
                    
                    if mode_dolomite_freshwater:
                        phi_dolomite_freshwater = (dt_log - dt_matrix_dolomite) / (dt_fluid_freshwater - dt_matrix_dolomite)
                        row_data['Sonic_Dolomite_Freshwater'] = phi_dolomite_freshwater * correction_oil
                        
                    # Add similar conditions for other checkboxes (e.g., mode_limestone_freshwater, mode_dolomite_freshwater, etc.)
                    data.append(row_data)
                
                if mode == 'Gas Correction':
                      
                    if mode_sandstone_seawater:
                        phi_sandstone_seawater = (dt_log - dt_matrix_sandstone) / (dt_fluid_seawater - dt_matrix_sandstone)
                        row_data['Sonic_Sandstone_Seawater'] = phi_sandstone_seawater * correction_gas
                    
                    if mode_limestone_seawater:
                        phi_limestone_seawater = (dt_log - dt_matrix_limestone) / (dt_fluid_seawater - dt_matrix_limestone)
                        row_data['Sonic_Limestone_Seawater'] = phi_limestone_seawater * correction_gas
                    
                    if mode_dolomite_seawater:
                        phi_dolomite_seawater = (dt_log - dt_matrix_dolomite) / (dt_fluid_seawater - dt_matrix_dolomite)
                        row_data['Sonic_Dolomite_Seawater'] = phi_dolomite_seawater * correction_gas
                    
                    if mode_sandstone_freshwater:
                        phi_sandstone_freshwater = (dt_log - dt_matrix_sandstone) / (dt_fluid_freshwater - dt_matrix_sandstone)
                        row_data['Sonic_Sandstone_Freshwater'] = phi_sandstone_freshwater * correction_gas
                    
                    if mode_limestone_freshwater:
                        phi_limestone_freshwater = (dt_log - dt_matrix_limestone) / (dt_fluid_freshwater - dt_matrix_limestone)
                        row_data['Sonic_Limestone_Freshwater'] = phi_limestone_freshwater * correction_gas
                    
                    if mode_dolomite_freshwater:
                        phi_dolomite_freshwater = (dt_log - dt_matrix_dolomite) / (dt_fluid_freshwater - dt_matrix_dolomite)
                        row_data['Sonic_Dolomite_Freshwater'] = phi_dolomite_freshwater * correction_gas
                        
                    # Add similar conditions for other checkboxes (e.g., mode_limestone_freshwater, mode_dolomite_freshwater, etc.)
                    data.append(row_data)
                    
      # Create the DataFrame with appropriate columns
        las_df_revised = pd.DataFrame(data)
        if mode_average:
          las_df_revised['Average Porosity'] = las_df_revised.iloc[:, 2:].mean(axis=1)  
    
        # Display the DataFrame as a presentable Excel-like table      
        if data == [] or selected_column == "DEPTH":
          for depth in (las_df["DEPTH"]):
            las_temporary = {"Depth": depth}
            temporary.append(las_temporary)
              
          temp = pd.DataFrame(temporary)
          st.subheader('Data Sets:')
          st.dataframe(temp)
        else:
          st.subheader('Data Sets:')
          st.dataframe(las_df_revised)
     

        

        
    if selected_tab == "Log Visualization":   
        # Default values for visualization
        plot_h_fig1 = 27
        plot_w_fig1 = 22
        plot_h_fig23 = 12
        plot_w_fig23 = 16
        title_size = 12
        title_height = 1.0
        line_width = 1
        dt_color = 'black'
        trackname_1 = f'Sonic Log\n{unit_curve}'
        trackname_2 = 'Sonic Porosity\np.u.'
        trackname_3 = 'Result\np.u.'
    
        # Sidebar for user input
        st.sidebar.header("Depth Selection")
        top_depth = st.sidebar.number_input('Top Depth', min_value=0.00, value=start_depth, step=100.00, key="top_depth")
        bot_depth = st.sidebar.number_input('Bottom Depth', min_value=0.00, value=stop_depth, step=100.00, key="bot_depth")
    
        st.sidebar.header("Scale Setting (Track 1)")
        dt_left = st.sidebar.number_input('Left Scale', min_value=0.00, max_value=1000.00, value=140.00, step=5.0, key="dt_left")
        dt_right = st.sidebar.number_input('Right Scale', min_value=0.00, max_value=1000.00, value=40.00, step=5.0, key="dt_right")
        grid_num_1 = st.sidebar.number_input('Number of Grids', min_value=0, value=10, step=1, key="grid_num_1")
    
        st.sidebar.header("Scale Setting (Track 2)")
        phis_left = st.sidebar.number_input('Left Scale', min_value=-0.151, max_value=1.051, value=0.5, step=0.05, key="phis_left")
        phis_right = st.sidebar.number_input('Right Scale', min_value=-0.151, max_value=1.051, value=-0.15, step=0.05, key="phis_right")
        grid_num_2 = st.sidebar.number_input('Number of Grids', min_value=0, value=10, step=1, key="grid_num_2")
    
        st.sidebar.header("Scale Setting (Track 3)")
        result_left = st.sidebar.number_input('Left Scale', min_value=-0.151, max_value=1.51, value=1.15, step=0.05, key="result_left")
        result_right = st.sidebar.number_input('Right Scale', min_value=-0.151, max_value=1.51, value=-0.15, step=0.05, key="result_right")
        grid_num_3 = st.sidebar.number_input('Number of Grids', min_value=0, value=10, step=1, key="grid_num_3")    
        
        # Create a subplot with 1 row and 3 columns
        fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(plot_w_fig1, plot_h_fig1), sharey=True)
        
        # # Set the super title for the entire figure
        # fig.suptitle("Sonic Log Interpretation")
        if data == [] or selected_column == "DEPTH":
          ax1 = plt.subplot2grid((1, 3), (0, 0), rowspan=1, colspan=1)
          ax2 = plt.subplot2grid((1, 3), (0, 1), rowspan=1, colspan=1)
          ax3 = plt.subplot2grid((1, 3), (0, 2), rowspan=1, colspan=1)
          st.subheader('Log Visualization')
          st.pyplot(fig)
        else:
            # =============================================================================
            # Subplot 1
            ax1 = plt.subplot2grid((1, 3), (0, 0), rowspan=1, colspan=1)
        
            # Sonic Log Reading track
            ax1.plot(las_df_revised['Sonic Log Reading'], las_df_revised['Depth'], color=dt_color, lw=line_width)
            ax1.set_xlabel(trackname_1)
            ax1.set_xlim(dt_left, dt_right)
            ax1.set_ylim(bot_depth, top_depth)
            ax1.xaxis.label.set_color(dt_color)
            ax1.tick_params(axis='x', colors=dt_color)
            ax1.spines["top"].set_edgecolor(dt_color)
            ax1.spines["top"].set_position(("axes", 1.02))
        
            # Calculate the middle value
            dt_middle = (dt_left + dt_right) / 2
        
            # Calculate the grid interval
            grid_interval = (dt_right - dt_left) / (grid_num_1 - 1)
        
            # Generate the list of x-axis tick positions
            xtick_positions = [round(dt_left, 2), round(dt_middle, 2), round(dt_right, 2)]
        
            # Generate the list of grid positions
            grid_positions = np.linspace(dt_left, dt_right, num=grid_num_1)
        
            # Set the x-axis ticks and labels
            ax1.set_xticks(xtick_positions)
            ax1.set_xticklabels([f"{x:.2f}" for x in xtick_positions])
        
            # Set the grid lines
            ax1.set_xticks(grid_positions, minor=True)
            ax1.grid(which='minor', linestyle='--', linewidth=0.5)
        
            # Major and minor grid lines
            ax1.grid(which='major', color='silver', linestyle='-')
            ax1.grid(which='minor', color='lightgrey', linestyle=':', axis='y')
            ax1.xaxis.set_ticks_position("top")
            ax1.xaxis.set_label_position("top")
        
            # =============================================================================
            # Subplot 2
            ax2 = plt.subplot2grid((1, 3), (0, 1), rowspan=1, colspan=1)
        
            # Select all columns in las_df_revised except "Depth" and "Sonic Log Reading"
            columns_to_plot = [col for col in las_df_revised.columns if col not in ["Depth", "Sonic Log Reading"]]
        
        
            # Plot the selected columns against 'Depth'
            for column in columns_to_plot:
                ax2.plot(las_df_revised[column], las_df_revised['Depth'], label=column)
        
            ax2.set_xlabel(trackname_2)
            ax2.set_xlim(phis_left, phis_right)
            ax2.set_ylim(bot_depth, top_depth)
            ax2.xaxis.label.set_color(dt_color)
            ax2.tick_params(axis='x', colors=dt_color)
            ax2.spines["top"].set_edgecolor(dt_color)
            ax2.spines["top"].set_position(("axes", 1.02))
        
            # Calculate the middle value
            phis_middle = (phis_left + phis_right) / 2
        
            # Calculate the grid interval
            grid_interval = (phis_right - phis_left) / (grid_num_2 - 1)
        
            # Generate the list of x-axis tick positions
            xtick_positions = [round(phis_left, 2), round(phis_middle, 2), round(phis_right, 2)]
        
            # Generate the list of grid positions
            grid_positions = np.linspace(phis_left, phis_right, num=grid_num_2)
        
            # Set the x-axis ticks and labels
            ax2.set_xticks(xtick_positions)
            ax2.set_xticklabels([f"{x:.2f}" for x in xtick_positions])
        
            # Set the grid lines
            ax2.set_xticks(grid_positions, minor=True)
            ax2.grid(which='minor', linestyle='--', linewidth=0.5)
        
            # Major and minor grid lines
            ax2.grid(which='major', color='silver', linestyle='-')
            ax2.grid(which='minor', color='lightgrey', linestyle=':', axis='y')
            ax2.xaxis.set_ticks_position("top")
            ax2.xaxis.set_label_position("top")
        
            # Add a legend to distinguish different columns
            ax2.legend()
        
        
            # Subplot 3
            ax3 = plt.subplot2grid((1, 3), (0, 2), rowspan=1, colspan=1)
            
            if mode == "Average":
                for column in columns_to_plot:
                    ax3.plot(las_df_revised['Average Porosity'], las_df_revised['Depth'], label="Max Value", color=dt_color)
        
            else:
                # Select all columns in las_df_revised except "Depth" and "Sonic Log Reading"
                columns_to_plot = [col for col in las_df_revised.columns if col not in ["Depth", "Sonic Log Reading"]]
            
                # Create an empty list to store the maximum values
                max_values = []
            
                # Iterate over the rows in the DataFrame
                for index, row in las_df_revised.iterrows():
                    # Initialize the maximum value as negative infinity
                    max_value = float('-inf')
                    
                    # Iterate over the columns you want to compare
                    for column in columns_to_plot:
                        # Get the value from the current column
                        value = row[column]
                        
                        # Update the maximum value if the current value is greater
                        if value > max_value:
                            max_value = value
                    
                    # Append the maximum value to the list
                    max_values.append(max_value)
            
                # Add the 'Max Value' column to the DataFrame and rename it
                max_values_df = pd.DataFrame(max_values, columns=["Max Value"])
            
                # Now you can use 'Max Value' in the plot
                ax3.plot(max_values_df['Max Value'], las_df_revised['Depth'], label="Max Value", color=dt_color)
        
                ##area-fill sand and shale for VSH
            ax3.fill_betweenx(las_df_revised['Depth'], -0.15, 0, interpolate=False, color = 'orange', linewidth=0, alpha=0.5, hatch = '=-')
            ax3.fill_betweenx(las_df_revised['Depth'], 0, 0.467, interpolate=False, color = 'green', linewidth=0, alpha=0.5, hatch = 'b')
            ax3.fill_betweenx(las_df_revised['Depth'], 0.467, 1, interpolate=False, color = 'gold', linewidth=0, alpha=0.5, hatch = 'o')
            ax3.fill_betweenx(las_df_revised['Depth'], 1, 1.51, interpolate=False, color = 'red', linewidth=0, alpha=0.5, hatch = 'x')
        
        
            ax3.set_xlabel(trackname_3)
            ax3.set_xlim(result_left, result_right)
            ax3.set_ylim(bot_depth, top_depth)
            ax3.xaxis.label.set_color(dt_color)
            ax3.tick_params(axis='x', colors=dt_color)
            ax3.spines["top"].set_edgecolor(dt_color)
            ax3.spines["top"].set_position(("axes", 1.02))
        
            # Calculate the middle value
            result_middle = (result_left + result_right) / 2
        
            # Calculate the grid interval
            grid_interval = (result_right - result_left) / (grid_num_3 - 1)
        
            # Generate the list of x-axis tick positions
            xtick_positions = [round(result_left, 2), round(result_middle, 2), round(result_right, 2)]
        
            # Generate the list of grid positions
            grid_positions = np.linspace(result_left, result_right, num=grid_num_3)
        
            # Set the x-axis ticks and labels
            ax3.set_xticks(xtick_positions)
            ax3.set_xticklabels([f"{x:.2f}" for x in xtick_positions])
        
            # Set the grid lines
            ax3.set_xticks(grid_positions, minor=True)
            ax3.grid(which='minor', linestyle='--', linewidth=0.5)
        
            # Major and minor grid lines
            ax3.grid(which='major', color='silver', linestyle='-')
            ax3.grid(which='minor', color='lightgrey', linestyle=':', axis='y')
            ax3.xaxis.set_ticks_position("top")
            ax3.xaxis.set_label_position("top")
            
            pdf_filename = "visualization_figures.pdf"
            pdf_pages = PdfPages(pdf_filename)
    
          
            # Show the plot in Streamlit
            st.subheader('Log Visualization')
            st.pyplot(fig)
            pdf_pages.savefig(fig)
            plt.close(fig)        
            
            #Legend for Result
            st.markdown('''
                     Corresponding porosity value for each color:
                     \nGreen = 0 to 0.476,
                     \nYellow = 0.476 to 1,
                     \nOrange = Less than 0,
                     \nRed = More than 1
                         ''')
            
            st.subheader('Depth vs Sonic Porosity')
            columns_to_plot = [col for col in las_df_revised.columns if col not in ["Depth", "Sonic Log Reading"]]
        
            # Create a figure and axis object
            fig2, ax = plt.subplots(figsize=(plot_w_fig23, plot_h_fig23))
        
            # Plot the selected columns against 'Depth' in a line graph
            for column in columns_to_plot:
                ax.plot(las_df_revised['Depth'], las_df_revised[column], label=column)
        
            # Set labels and title
            ax.set_xlabel('Depth')
            ax.set_ylabel('Sonic Porosity')  # You can customize the label as needed
            ax.set_title('')
        
            # Add a legend
            ax.legend()
        
            # Show the plot
            st.pyplot(fig2)
            pdf_pages.savefig(fig2)
            plt.close(fig2)
        
            st.subheader('Sonic Log Reading vs Sonic Porosity')
            columns_to_plot = [col for col in las_df_revised.columns if col not in ["Depth", "Sonic Log Reading"]]
        
            # Create a figure and axis object
            fig3, ax = plt.subplots(figsize=(plot_w_fig23, plot_h_fig23))
        
            # Plot the selected columns against 'Depth' in a line graph

            for column in columns_to_plot:
                ax.plot(las_df_revised['Sonic Log Reading'], las_df_revised[column], label=column)
            
            # Set labels and title
            ax.set_xlabel('Sonic Log Reading')
            ax.set_ylabel('Sonic Porosity')  # You can customize the label as needed
            ax.set_title('')
        
            # Add a legend
            ax.legend()
        
            # Show the plot
            st.pyplot(fig3)
            pdf_pages.savefig(fig3)
            plt.close(fig3)
            pdf_pages.close()
            
            
            st.markdown('**Download Result:**')
            with open(pdf_filename, "rb") as pdf_file:
                st.download_button("Download", pdf_file.read(), key="pdf_button", mime="application/pdf")

        if data == [] or selected_column == "DEPTH":
            st.warning('Please select other curve data.')
        else:
            formeval_mode = st.sidebar.checkbox("Formation Evaluation")
            need_calibration = False
            have_anomaly = False
            need_correction = False
            no_error = False
        
            def result_calibration():
                st.markdown('''**Negative porosity value. Porosity should range between 0 to 1.**
                            \nPossible reason:
                            \nWrong matrix used.
                            \nCycle Skipping
                                ''')
        
            def result_anomaly():
                st.markdown('''**More than 1 porosity value. Reading anomalies detected.**
                            \nPossible reason:
                            \nCycle Skipping
                            \nBorehole condition problem occurance. The holes might be larger than about 24 in. for common rocks.
                            \nThe borehole is air-filled or if the mud is gas-cut
                            ''')
        
            def result_correction():
                st.markdown('''**Overestimate porosity value. Correction should be applied.**
                            \nPossible reason:
                            \nUncompacted
                            \nHydrocarbon present
                            \nComplex lithology
                            ''')
        
            def result_good():
                st.markdown('''**Normal sonic porosity reading.**''')
        
        
            if formeval_mode:
              st.divider()
              st.subheader('Findings:')
              for max_value in max_values_df['Max Value']:
                  if max_value < 0 and not need_calibration:
                      need_calibration = True
                      no_error = False
                      result_calibration()

                  if max_value > 1 and not have_anomaly:
                      have_anomaly = True
                      no_error = False
                      result_anomaly()

                  if 0.467 < max_value < 1 and not need_correction:
                      need_correction = True
                      no_error = False
                      result_correction()

                  if 0 < max_value < 0.467 and not need_calibration and not have_anomaly and not need_correction and not no_error:
                      no_error = True
                      need_calibration = False
                      have_anomaly = False
                      need_correction = False
                      result_good()
                      break
