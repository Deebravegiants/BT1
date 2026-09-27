# [M] CVE-2021-28166

## Summary
Severity: Medium
Advisory: CVE-2021-28166
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-07
Source: https://osv.dev/vulnerability/CVE-2021-28166
Type: osv

## Details
In Eclipse Mosquitto version 2.0.0 to 2.0.9, if an authenticated client that had connected with MQTT v5 sent a crafted CONNACK message to the broker, a NULL pointer dereference would occur.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=572608
