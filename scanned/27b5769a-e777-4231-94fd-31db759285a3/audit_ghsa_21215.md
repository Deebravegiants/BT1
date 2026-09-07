# [M] Microweber before 1.2.21 allows attacker to bypass IP detection to brute-force password

## Summary
Severity: Medium
Advisory: GHSA-9wqr-9787-p4rf
CVE: CVE-2022-2368
CWE: CWE-290
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-07-12
Source: https://github.com/advisories/GHSA-9wqr-9787-p4rf
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.2.21

## Details
In the login API, an IP address will by default be blocked when the user tries to login incorrectly more than 5 times. However, a bypass to this mechanism is possible by abusing a X-Forwarded-For header to bypass IP detection and perform a password brute-force. A patch for this issue is available in Microweber version 1.2.21.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2368
- https://github.com/microweber/microweber/commit/53c000ccd5602536e28b15d9630eb8261b04a302
- https://github.com/microweber/microweber
- https://huntr.dev/bounties/a9595eda-a5e0-4717-8d64-b445ef83f452
