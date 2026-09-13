# [C] Project Firefly III has incorrect access control in the webhook management component

## Summary
Severity: Critical
Advisory: GHSA-9mmg-q95p-gp67
CVE: CVE-2026-50886
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-9mmg-q95p-gp67
Type: github-advisory

## Affected
- Packagist: `grumpydictator/firefly-iii` — affected >=0

## Details
Incorrect access control in the webhook management component of Project Firefly III v6.5.9 allows attackers to scan internal resources via a crafted POST request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50886
- https://gist.github.com/pyuysig/f5395f90753ba652835ba9c6abf4c4ae
- https://github.com/firefly-iii/firefly-iii
