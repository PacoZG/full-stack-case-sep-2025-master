# Coding Exercise: Signal Data Ingestion

Welcome! Excited to have you solving our case! The aim here is to get you familiarised with this provided repo, see how you build basic features and lay grounds on our potential live coding session.

## Core Requirements

**Time:** Aim for 4 to 5 hours. Focus on a well structured solution and big picture.

**If for some reason you get stuck somewhere:** do not burn endless amount of time solving the annoying bugs but instead focus on building the big picture and that you at least have code that runs.

**Repository:** Build upon the provided full stack FastAPI project template. Feel free to add libraries as you like and remember to justify their use.

**Execution:** Please find the instructions on how to execute and locally deploy the repo in `README.md` file. Add a clear note in `NOTES.md` if you change something related to the docker compose setup.

**Submission:** Please find your deadline for submission in the email where you got link to this case.

**Focus:** We value simplicity over complexity, robustness and clear structure. However, pay attention to your coding practises as well. The code should be easy to follow and understand.

**Allowed tools:** In this exercise as well as the potential future live coding session, you are free to use any tools or development environments you prefer. Select the tools that support your work best.

**Questions:** Contact us at mikko@rotomate.ai or jesse@rotomate.ai for further questions.

## The Task: Implementing file upload and processing

Build a system to ingest signal data files and display basic information about the uploaded data.

*   Create a feature for the users to upload files. The upload should be accessible from the UI.
*   Create a basic view that just shows what files have been uploaded
*   Three example upload files are provided in this [Google Drive folder](https://drive.google.com/drive/folders/1MQRSvz9C1DQNJ_objdM-nnGACIETeIV4). Select one of the files and implement the upload functionality for that data type.
*   All uploaded files contain signal data measured with accelerometers installed on various industrial equipment
*   **Signal Data Structure:** Each file contains information for one or more measurement points at different timestamps. Each data point includes at least the following:
    *   `facility_name` (string)
    *   `facility_section_name` (string)
    *   `machine_name` (string) name of the asset or machine that is monitored
    *   `measurement_point_name` (string) name of the measurement or sensor location
    *   `measured_at` (timestamp or datetime string) The time when the signal was measured
    *   `rotating_speed` (float provided in various units such as Hz or RPM)
    *   `signal` (an array of floating point numbers)
    *   `signal_unit` (string, e.g., "g", "mm/s")
    *   `sampling_rate_hz` (float, e.g., 25600.0)
*   Notice that different files can have different names and formats for each data field. The files can also have extra fields on top of these. You can ignore those and just focus on the data above.
  
Overall the system should also fulfill these requirements:
*   **Extensibility:** These examples are just currently know versions of the file type. Design your system considering that future requirements might introduce variations or entirely new data structures. The core data ingestion mechanism should be adaptable.
*   **Scale:**  Consider that one file can include thousands of signal values (i.e. floating point arrays) with length of +100k. How to design smooth UX with these larger data amounts? 
*   **Data Management:**
    *   Signal data needs to be queried frequently e.g. for visualization or other processing.
    *   It will also be processed often with both various aggregating math functions (e.g., mean, max over time) but also more advanced signal processing methods.

It is completely understandable if the solution does not fully fill all of these requirements but be ready to discuss these constraints when presenting the case results.

### Happy case solving!