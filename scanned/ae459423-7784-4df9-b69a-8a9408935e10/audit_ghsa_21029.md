# [M] OctoPrint vulnerable to Insufficient Session Expiration.

## Summary
Severity: Medium
Advisory: GHSA-937f-qh3w-6g87
CVE: CVE-2022-2888
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-937f-qh3w-6g87
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.8.3

## Details
If an attacker comes into the possession of a victim's OctoPrint session cookie through whatever means, the attacker can use this cookie to authenticate as long as the victim's account exists. This issue is fixed in version 1.8.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2888
- https://github.com/octoprint/octoprint/commit/40e6217ac1a85cc5ed592873ae49db01d3005da4
- https://github.com/octoprint/octoprint
- https://github.com/pypa/advisory-database/tree/main/vulns/octoprint/PYSEC-2022-282.yaml
- https://huntr.dev/bounties/d27d232b-2578-4b32-b3b4-74aabdadf629
