# [M] CVE-2021-34431

## Summary
Severity: Medium
Advisory: CVE-2021-34431
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-22
Source: https://osv.dev/vulnerability/CVE-2021-34431
Type: osv

## Details
In Eclipse Mosquitto version 1.6 to 2.0.10, if an authenticated client that had connected with MQTT v5 sent a crafted CONNECT message to the broker a memory leak would occur, which could be used to provide a DoS attack against the broker.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=573191
