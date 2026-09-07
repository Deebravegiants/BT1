# [H] Weak Password Recovery Mechanism for Forgotten Password

## Summary
Severity: High
Advisory: GHSA-c32w-3cqh-f6jx
CVE: CVE-2021-25957
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-c32w-3cqh-f6jx
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <14.0.0

## Details
In “Dolibarr” application, v2.8.1 to v13.0.2 are vulnerable to account takeover via password reset functionality. A low privileged attacker can reset the password of any user in the application using the password reset link the user received through email when requested for a forgotten password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25957
- https://github.com/Dolibarr/dolibarr/commit/87f9530272925f0d651f59337a35661faeb6f377
- https://github.com/Dolibarr/dolibarr
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25957
