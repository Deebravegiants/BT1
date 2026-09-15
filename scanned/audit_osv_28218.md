# [M] Azure C SDK Integer Wraparound Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2024-29195
Aliases: GHSA-m8wp-hc7w-x4xg
CVSS: 6.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:L)
Published: 2024-03-26
Source: https://osv.dev/vulnerability/CVE-2024-29195
Type: osv

## Details
The azure-c-shared-utility is a C library for AMQP/MQTT communication to Azure Cloud Services. This library may be used by the Azure IoT C SDK for communication between IoT Hub and IoT Hub devices. An attacker can cause an integer wraparound or under-allocation or heap buffer overflow due to vulnerabilities in parameter checking mechanism, by exploiting the buffer length parameter in Azure C SDK, which may lead to remote code execution. Requirements for RCE are 1. Compromised Azure account allowing malformed payloads to be sent to the device via IoT Hub service, 2. By passing IoT hub service max message payload limit of 128KB, and 3. Ability to overwrite code space with remote code. Fixed in commit https://github.com/Azure/azure-c-shared-utility/commit/1129147c38ac02ad974c4c701a1e01b2141b9fe2.

## References
- https://github.com/Azure/azure-c-shared-utility/security/advisories/GHSA-m8wp-hc7w-x4xg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29195.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-29195
- https://github.com/Azure/azure-c-shared-utility/commit/1129147c38ac02ad974c4c701a1e01b2141b9fe2
