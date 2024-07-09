import streamlit as st
import subprocess
import os
import time

# Set config
st.set_page_config(page_title="Remote servers", page_icon=":file_folder:")

mount, unmount = st.tabs(["Mount server", "Unmount server"])

with mount:
    # Mount server page
    st.title(":file_folder: \t Mount remote server")

    server = st.selectbox("Select NAS server", ["TU Delft", "Oxford"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if server == "TU Delft":
        domain = "sftp.tudelft.nl"
        remote_path = "/staff-groups/tnw/bn/nd/"
        local_path = "/mnt/TUDelft/"
    elif server == "Oxford":
        domain = "winfe.physics.ox.ac.uk"
        remote_path = "/dfs/DAQ/CondensedMatterGroups/DekkerGroup/"
        local_path = "/mnt/Oxford/"

    command = f"#!/bin/bash\nsudo sshfs -o allow_other,reconnect,password_stdin {username}@{domain}:{remote_path} {local_path} <<< '{password}'"
    mounted = True if len(os.listdir(local_path)) > 0 else False

    if mounted:
        st.warning("Server is already mounted.")
    else:
        if (username != "") & (password != ""):
            if st.button("Connect"):
                # Run the command and capture the output and error
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable="/bin/bash")
                stdout, stderr = process.communicate()

                # Decode the output and error
                stdout = stdout.decode('utf-8')
                stderr = stderr.decode('utf-8')

                # Show the output and error
                if stdout != "":
                    st.info(stdout)
                if stderr != "":
                    st.error(stderr)
                else:
                    st.balloons()
                    st.info(f"Successfully mounted server {server}")

                    # Open the server
                    with st.spinner(f'Opening folder at: {local_path} ...'):
                        time.sleep(2)
                        os.system(f"nautilus {local_path}")
        else:
            st.warning("Please write username and password")

with unmount:
    # Mount server page
    st.title(":file_folder: \t Unmount remote server")

    server = st.selectbox("Select NAS server", ["TU Delft", "Oxford"], key="umount")
    
    if server == "TU Delft":
        local_path = "/mnt/TUDelft/"
    elif server == "Oxford":
        local_path = "/mnt/Oxford/"

    command = f"sudo umount {local_path}"

    mounted = True if len(os.listdir(local_path)) > 0 else False

    if mounted:
        if st.button("Unmount"):
            # Run the command and capture the output and error
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable="/bin/bash")
            stdout, stderr = process.communicate()

            # Decode the output and error
            stdout = stdout.decode('utf-8')
            stderr = stderr.decode('utf-8')

            # Show the output and error
            if stdout != "":
                st.info(f"Standard Output:\n{stdout}" )
            if stderr != "":
                st.error(f"{stderr}")
            else:
                st.balloons()
                st.info(f"Successfully unmount server {server}")
    else:
        st.warning(f"Server {server} is not mounted")


