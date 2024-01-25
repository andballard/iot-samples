@description('Location of all resources')
param location string = 'East US2'
param docker_image string = 'DOCKER|acrsimplant.azurecr.io/mag_mqtt_sim:latest'
param sim_cert_path string = ''
param sim_key_path string = ''
param csv_path string = ''
//param mqtt_host string = 'simulated-plant-eg.eastus-1.ts.eventgrid.azure.net'
//param mqtt_port string = '8883'
//param mqtt_topic string = 'alice-springs-solution/data/opc-ua-connector/opc-ua-connector-0/robot'
@secure()
param dockerRegistryServerName string = 'acrsimplant.azurecr.io'
param dockerRegistryUserName string = 'acrsimplant'
@secure()
param dockerRegistryPassword string = '' // Replace with your secret reference or leave as empty string



// get random string for unique name
var random_string = toLower(uniqueString(resourceGroup().id))
var server_farm_name = 'ov-mqtt-app-service-plan-${random_string}'
var app_service_name = 'ov-mqtt-simulator-${random_string}'
var dockerImage = 'DOCKER|${docker_image}'

var app_settings = [
  {
    name: 'CSV_PATH'
    value: '/app/source/mqtt_sim/pos.csv'
  }
  {
    name: 'SIM_CERT_PATH'
    value: '/app/source/mqtt_sim/sim-authn-ID.pem'
  }
  {
    name: 'SIM_KEY_PATH'
    value: '/app/source/mqtt_sim/sim-authn-ID.key'
  }
  {
    name: 'OMNI_SCRIPT'
    value: '/app/source/mqtt_sim/app.py'
  }
  {
    name: 'DOCKER_REGISTRY_SERVER_PASSWORD'
    value: dockerRegistryPassword
  }
  {
    name: 'DOCKER_REGISTRY_SERVER_URL'
    value: dockerRegistryServerName
  }
  {
    name: 'DOCKER_REGISTRY_SERVER_USERNAME'
    value: dockerRegistryUserName
  }
]

resource ov_connector_server_farm 'Microsoft.Web/serverfarms@2021-03-01' = {
  name: server_farm_name
  location: location
  tags: {
    'Created By': 'Horizon - OPC Omniverse MQTT Connector'
    'hidden-title':'IMV - OPC Omniverse MQTT Connector'
  }
  kind:'linux'
  properties: {
    perSiteScaling: false
    elasticScaleEnabled: false
    maximumElasticWorkerCount: 1
    isSpot: false
    reserved: true
    isXenon: false
    hyperV: false
    targetWorkerCount: 0
    targetWorkerSizeId: 0
    zoneRedundant: false
  }
  sku: {
    name: 'B3'
    tier: 'Basic'
    size: 'B3'
    family: 'B'
    capacity: 1
  }
}

resource ov_connector_app_service 'Microsoft.Web/sites@2021-02-01' = {
  name: app_service_name
  location: location
  kind: 'app,linux,container'
  properties: {
    serverFarmId: ov_connector_server_farm.id
    siteConfig: {
      linuxFxVersion: dockerImage
      alwaysOn: true
      http20Enabled: false
      scmType: 'LocalGit'
      appSettings: app_settings
    }
    httpsOnly: true
  }
  identity: {
    type: 'SystemAssigned'
  }
}

output appServiceUrl string = ov_connector_app_service.properties.defaultHostName