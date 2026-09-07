# [C] Ray OS Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-h3xg-wv58-5p43
CVE: CVE-2023-6019
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-16
Source: https://github.com/advisories/GHSA-h3xg-wv58-5p43
Type: github-advisory

## Affected
- PyPI: `ray` — affected >=0 <2.8.1

## Details
A command injection exists in Ray's cpu_profile URL parameter allowing attackers to execute os commands on the system running the ray dashboard remotely without authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6019
- https://github.com/ray-project/ray
- https://github.com/ray-project/ray/releases/tag/ray-2.8.1
- https://huntr.com/bounties/d0290f3c-b302-4161-89f2-c13bb28b4cfe
- https://www.anyscale.com/blog/update-on-ray-cves-cve-2023-6019-cve-2023-6020-cve-2023-6021-cve-2023-48022-cve-2023-48023
