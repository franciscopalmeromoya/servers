import streamlit as st
import subprocess
import os
import time
import yaml

def readConfig(filepah : str) -> dict:
    try:
        with open(filepah, "r") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError as e:
        st.warning("Please, provide a valid config file path.")
        return dict()
    else:
        return config

def validateConfig(config : dict) -> bool:
    for server in config.keys():
        data = config[server]
        missing =  set(["domain", "local_path", "remote_path"]) - set(data.keys())
        if len(list(missing)) > 0:
            st.warning(f"The following attributes are required to set a connection in {server} server:")
            for att in list(missing):
                st.warning(att)
            return False
        else:
            return True

def main():

    # Create tabs
    mount, unmount, manual = st.tabs(["Mount server", "Unmount server", "User manual"])

    # Read config file
    config_path = "config.yaml"
    config = readConfig(config_path)

    # Validate config file
    if not validateConfig(config):
        return 0
    
    # Set servers list
    servers = list(config.keys())

    with manual:
        readme_path = os.path.join("docs", "MANUAL.md")
        try:
            with open(readme_path, "r", encoding="utf-8") as file:
                readme = file.read()
        except FileNotFoundError as e:
            st.warning("Please, provide a valid readme file path.")
        else:
            st.write(readme)

    with mount:
        # Mount server page
        st.title(":file_folder: \t Mount remote server")

        # User inputs: server
        server = st.selectbox("Select NAS server", servers)

        # Required server information
        domain = config[server]["domain"]
        remote_path = config[server]["remote_path"]
        local_path = config[server]["local_path"]

        mounted = True if len(os.listdir(local_path)) > 0 else False

        if mounted:
            st.warning("Server is already mounted.")
            if st.button("Refresh"):
                pass
        else:
            # User inputs: credentials
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            command = f"#!/bin/bash\nsudo sshfs -o allow_other,reconnect,password_stdin {username}@{domain}:{remote_path} {local_path} <<< '{password}'"
            if st.button("Connect"):
                if (username != "") & (password != ""):
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
                        with st.spinner('Opening folder ...'):
                            time.sleep(2)
                            try:
                                result = subprocess.run(["nautilus", local_path])
                            except subprocess.CalledProcessError as e:
                                st.error(e)

                else:
                    st.warning("Please write username and password")

    with unmount:
        # Mount server page
        st.title(":file_folder: \t Unmount remote server")

        # User inputs
        server = st.selectbox("Select NAS server", servers, key="umount")
        
        # Required server information
        local_path = config[server]["local_path"]

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

if __name__ == "__main__":
    # Set config
    st.set_page_config(page_title="Remote servers", page_icon=":file_folder:")  
    main()


