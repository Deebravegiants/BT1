# [H] CVE-2021-22547

## Summary
Severity: High
Advisory: CVE-2021-22547
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-04
Source: https://osv.dev/vulnerability/CVE-2021-22547
Type: osv

## Details
In IoT Devices SDK, there is an implementation of calloc() that doesn't have a length check. An attacker could pass in memory objects larger than the buffer and wrap around to have a smaller buffer than required, allowing the attacker access to the other parts of the heap. We recommend upgrading the Google Cloud IoT Device SDK for Embedded C used to 1.0.3 or greater.

## References
- https://github.com/GoogleCloudPlatform/iot-device-sdk-embedded-c/blob/master/RELEASE-NOTES.md
- https://github.com/GoogleCloudPlatform/iot-device-sdk-embedded-c/pull/119
