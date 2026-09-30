# [H] CVE-2021-41039

## Summary
Severity: High
Advisory: CVE-2021-41039
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-12-01
Source: https://osv.dev/vulnerability/CVE-2021-41039
Type: osv

## Details
In versions 1.6 to 2.0.11 of Eclipse Mosquitto, an MQTT v5 client connecting with a large number of user-property properties could cause excessive CPU usage, leading to a loss of performance and possible denial of service.

## References
- https://www.debian.org/security/2023/dsa-5511
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=575314
