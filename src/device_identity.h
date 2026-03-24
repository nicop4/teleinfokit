#ifndef DEVICE_IDENTITY_H
#define DEVICE_IDENTITY_H

#include <Arduino.h>

class DeviceIdentity
{
public:
    static constexpr size_t UNIQUE_ID_SIZE = 30;
    static constexpr size_t AP_NAME_SIZE = 30;

    static void init();
    static const char *uniqueId();
    static const char *apName();

private:
    static void buildIdentity();

    static bool initialized;
    static char unique_id[UNIQUE_ID_SIZE];
    static char ap_name[AP_NAME_SIZE];
};

#endif /* DEVICE_IDENTITY_H */
