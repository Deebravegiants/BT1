# [M] CVE-2017-7653

## Summary
Severity: Medium
Advisory: CVE-2017-7653
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-05
Source: https://osv.dev/vulnerability/CVE-2017-7653
Type: osv

## Details
The Eclipse Mosquitto broker up to version 1.4.15 does not reject strings that are not valid UTF-8. A malicious client could cause other clients that do reject invalid UTF-8 strings to disconnect themselves from the broker by sending a topic string which is not valid UTF-8, and so cause a denial of service for the clients.

## References
- https://usn.ubuntu.com/4023-1/
- http://docs.oasis-open.org/mqtt/disallowed-chars/v1.0/disallowed-chars-v1.0.pdf
- https://lists.debian.org/debian-lts-announce/2018/09/msg00036.html
- https://www.debian.org/security/2018/dsa-4325
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=532113
