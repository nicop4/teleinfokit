#include "device_identity.h"

#if _HW_VER <= 4
  #include <ESP8266WiFi.h>
#elif _HW_VER == 5
  #include <WiFi.h>
#elif _HW_VER == 6
  #include <WiFi.h>
  #include <EthernetESP32.h>
#endif

bool DeviceIdentity::initialized = false;
char DeviceIdentity::unique_id[DeviceIdentity::UNIQUE_ID_SIZE] = {0};
char DeviceIdentity::ap_name[DeviceIdentity::AP_NAME_SIZE] = {0};

void DeviceIdentity::init()
{
    if (!initialized)
    {
        buildIdentity();
        initialized = true;
    }
}

const char *DeviceIdentity::uniqueId()
{
    init();
    return unique_id;
}

const char *DeviceIdentity::apName()
{
    init();
    return ap_name;
}

void DeviceIdentity::buildIdentity()
{
#if _HW_VER <= 4
    snprintf(unique_id, sizeof(unique_id), "teleinfokit-%06X", ESP.getChipId());
    snprintf(ap_name, sizeof(ap_name), "TeleInfoKit-%06X", ESP.getChipId());
#elif _HW_VER == 5
    const uint64_t mac = ESP.getEfuseMac();
    char macHex[13];
    snprintf(macHex, sizeof(macHex), "%012llX", static_cast<unsigned long long>(mac));

    const char *last6 = macHex + 6;
    snprintf(unique_id, sizeof(unique_id), "teleinfokit-%s", last6);
    snprintf(ap_name, sizeof(ap_name), "TeleInfoKit-%s", last6);
#elif _HW_VER == 6
    String mac = Ethernet.macAddress();
    mac.replace(":", "");
    String macLast6 = mac.length() >= 6 ? mac.substring(mac.length() - 6) : mac;

    unsigned long shortMac = strtoul(macLast6.c_str(), nullptr, 16);
    snprintf(unique_id, sizeof(unique_id), "teleinfokit-%06lX", shortMac);
    snprintf(ap_name, sizeof(ap_name), "TeleInfoKit-%06lX", shortMac);
#endif
}
