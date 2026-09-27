# [M] Absolute path traversal vulnerability in digdag server

## Summary
Severity: Medium
Advisory: GHSA-5mp4-32rr-v3x5
CVE: CVE-2024-25125
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-14
Source: https://github.com/advisories/GHSA-5mp4-32rr-v3x5
Type: github-advisory

## Affected
- Maven: `io.digdag:digdag-server` — affected >=0 <0.10.5.1

## Details
### Summary

Treasure Data's digdag workload automation system is susceptible to a path traversal vulnerability if it's configured to store log files locally.

### Impact

This issue may lead to Information Disclosure.

## References
- https://github.com/treasure-data/digdag/security/advisories/GHSA-5mp4-32rr-v3x5
- https://nvd.nist.gov/vuln/detail/CVE-2024-25125
- https://github.com/treasure-data/digdag/commit/eae89b0daf6c62f12309d8c7194454dfb18cc5c3
- https://github.com/treasure-data/digdag
