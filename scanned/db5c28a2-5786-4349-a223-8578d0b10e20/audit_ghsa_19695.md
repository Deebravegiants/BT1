# [H] Feast Cross-Origin Resource Sharing vulnerability

## Summary
Severity: High
Advisory: GHSA-wxpc-2674-rxvw
CVE: CVE-2024-11602
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-wxpc-2674-rxvw
Type: github-advisory

## Affected
- PyPI: `feast` — affected >=0

## Details
A Cross-Origin Resource Sharing (CORS) vulnerability exists in feast-dev/feast version 0.40.0. The CORS configuration on the agentscope server does not properly restrict access to only trusted origins, allowing any external domain to make requests to the API. This can bypass intended security controls and potentially expose sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11602
- https://github.com/feast-dev/feast
- https://huntr.com/bounties/7b24ecbe-0af7-4125-ab56-bce09786042e
