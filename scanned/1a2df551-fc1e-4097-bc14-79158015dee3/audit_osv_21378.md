# [H] CVE-2021-42559

## Summary
Severity: High
Advisory: CVE-2021-42559
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2021-42559
Type: osv

## Details
An issue was discovered in CALDERA 2.8.1. It contains multiple startup "requirements" that execute commands when starting the server. Because these commands can be changed via the REST API, an authenticated user can insert arbitrary commands that will execute when the server is restarted.

## References
- https://github.com/mitre/caldera/releases
- https://github.com/DrunkenShells/Disclosures/tree/master/CVE-2021-42559-Command%20Injection%20Via%20Configurations-MITRE%20Caldera
