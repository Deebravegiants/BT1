# [H] CVE-2021-34432

## Summary
Severity: High
Advisory: CVE-2021-34432
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-27
Source: https://osv.dev/vulnerability/CVE-2021-34432
Type: osv

## Details
In Eclipse Mosquitto versions 2.0.7 and earlier, the server will crash if the client tries to send a PUBLISH packet with topic length = 0.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=574141
