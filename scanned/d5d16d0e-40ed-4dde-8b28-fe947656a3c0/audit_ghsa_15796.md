# [C] RaspAP allows an attacker to escalate privileges

## Summary
Severity: Critical
Advisory: GHSA-q623-2j2j-23jj
CVE: CVE-2024-41637
CWE: CWE-269, CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-29
Source: https://github.com/advisories/GHSA-q623-2j2j-23jj
Type: github-advisory

## Affected
- Packagist: `billz/raspap-webgui` — affected >=0

## Details
RaspAP before 3.1.5 allows an attacker to escalate privileges: the www-data user has write access to the restapi.service file and also possesses Sudo privileges to execute several critical commands without a password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41637
- https://blog.0xzon.dev/2024-07-27-CVE-2024-41637
- https://github.com/RaspAP/raspap-webgui
