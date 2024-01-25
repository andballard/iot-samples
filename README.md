# Omniverse Kit App Template
 
[Omniverse Kit App Template](https://github.com/NVIDIA-Omniverse/kit-app-template) - is the place to start learning about developing Omniverse Apps.
This project contains everything necessary to develop and package an Omniverse App.
 
## Links
 
* Recommended: [Tutorial](https://docs.omniverse.nvidia.com/kit/docs/kit-app-template) for
getting started with application development.
* [Developer Guide](https://docs.omniverse.nvidia.com/dev-guide/latest/index.html).
 
## Build
 
1. Clone [this repo](https://github.com/andballard/iot-samples) to your local machine.
2. Open a command prompt and navigate to the root of your cloned repo.
3. Run `build.bat` to bootstrap your dev environment and build the application.
4. Run `_build\windows-x86_64\release\nova.iot_telemetry.bat` to open the kit application.
 
You should have now launched your simple kit-based application!
 
## Custom Extensions
The [main extension](./src/kit-app-template/source/extensions/msft.nova.usd_explorer/) is registered as msft.nova.usd_explorer. In this extension, we load the usd and other required dependencies.
 
The [robot arm extension](./src/kit-app-template/source/extensions/msft.nova.robot_controller/) is registerd as msft.nova.robot_controller. This extension handles robot arm movement by listening to incoming IoT data in the session layer.
 
The IoT [widget extension](./src/kit-app-template/source/extensions/msft.nova.iot_info_panel/) is registered as msft.nova.iot_info_panel. This extension is activated by clicking on the robot arm and also listens to the incoming IoT data from the session layer.
 
## Environment Settings
Name | Type | Required | Example
--- | --- | --- | --- |
robot_base_path | string | Y | /World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003 |
robot_joint_paths | string | Y | link1piv_003, link2piv_003, link3piv_003 |
omniverse_host | string | Y | contonso.azurenucleus.co.uk |

These settings are required for the application and must be present in the app package root folder.
 
## Robot Simulator
 
This repo contains a robot arm [simulator](./src/kit-app-template/source/mqtt_sim/) that can be used when the physical magnemotion data stream is not available. This module loops over data in a [csv](./src/kit-app-template/source/mqtt_sim/pos.csv) file and sends the data to the configured mqtt broker. The simulator can be deployed as a docker container in the cloud or ran locally for testing.
 
## Running robot simulator with Docker
 
To run the container with Docker, you need to set the environment variables using the `-e` option. Here's an example `docker run` command:
 
```shell
docker run -d \
  -e SIM_CERT_PATH='your_mqtt_cert_path' \
  -e SIM_KEY_PATH='your_mqtt_key_path' \
  -e CSV_PATH='your_csv_data' \
  --name your_container_name your_image_name
  ```
 
## Cloud deployment
 
This container can be deployed to the Azure Cloud and is designed to play nicely with Azure App Services + [Azure IoT Operations](https://learn.microsoft.com/en-us/azure/iot-operations/get-started/overview-iot-operations)
 
To deploy the simulator to the cloud you can use a powershell script and bicep template located [here](./src/kit-app-template/source/mqtt_sim/cloud/deploy.ps1).
 
> ⚠️ **Warning** This script is designed to be run from a powershell and has only been tested on windows. It may not work on other operating systems (or the devcontainer)
 
 
```bash
.\deploy.ps1 -resourceGroupName 'ov-connector' -location 'eastus2' -dockerImageName 'acrsimplant.azurecr.io/mag_mqtt_sim:1.0.4' -sim_cert_path 'your-cert-path' -sim_key_path 'your-key-path' -csv_path 'your-csv-path' -docker_registry_password  'YourAcrPassword'  -docker_registry_server_url 'acrsimplant.azurecr.io' -docker_registry_username 'acrsimplant'
```
 
This will run a bicep deployment which creates an azure app service which points to the docker image you specify - (hopefully, containing your mqtt_sim app.)
 
## Contributing
The source code for this repository is provided as-is and we are not accepting outside contributions.