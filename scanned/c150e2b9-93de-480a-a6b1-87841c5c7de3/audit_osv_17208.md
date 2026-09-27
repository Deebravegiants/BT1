# [C] CVE-2020-13702

## Summary
Severity: Critical
Advisory: CVE-2020-13702
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2020-06-11
Source: https://osv.dev/vulnerability/CVE-2020-13702
Type: osv

## Details
The Rolling Proximity Identifier used in the Apple/Google Exposure Notification API beta through 2020-05-29 enables attackers to circumvent Bluetooth Smart Privacy because there is a secondary temporary UID. An attacker with access to Beacon or IoT networks can seamlessly track individual device movement via a Bluetooth LE discovery mechanism.

## References
- https://blog.google/documents/70/Exposure_Notification_-_Bluetooth_Specification_v1.2.2.pdf
- https://github.com/google/exposure-notifications-internals/commit/8f751a666697
- https://github.com/google/exposure-notifications-internals/commit/8f751a666697c3cae0a56ae3464c2c6cbe31b69e
- https://github.com/normanluhrmann/infosec/raw/master/exposure-notification-vulnerability-20200611.pdf
- https://github.com/normanluhrmann/infosec/raw/master/exposure-notification-vulnerability-20200616-2.pdf
- https://github.com/normanluhrmann/infosec/raw/master/exposure-notification-vulnerability-20200616.pdf
