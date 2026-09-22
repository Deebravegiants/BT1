# [C] CVE-2020-35358

## Summary
Severity: Critical
Advisory: CVE-2020-35358
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-15
Source: https://osv.dev/vulnerability/CVE-2020-35358
Type: osv

## Details
DomainMOD domainmod-v4.15.0 is affected by an insufficient session expiration vulnerability. On changing a password, both sessions using the changed password and old sessions in any other browser or device do not expire and remain active. Such flaws frequently give attackers unauthorized access to some system data or functionality.

## References
- https://gist.github.com/anku-agar/0fec2ffd98308e550ce9b5d4b395d0d7
