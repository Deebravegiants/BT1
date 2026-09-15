# [M] OpenFGA's BatchCheck within-request deduplication produces incorrect authorization decisions via list-value cache-key collision

## Summary
Severity: Medium
Advisory: GHSA-jwvj-g8pc-cx45
CVE: CVE-2026-34972
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-jwvj-g8pc-cx45
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=1.8.0 <1.14.0

## Details
### Description

In OpenFGA, under specific conditions, BatchCheck calls with multiple checks sent for the same object, relation, and user combination can result in improper policy enforcement.

### Am I affected?

You are affected if you meet the following preconditions:
1. You execute **BatchCheck** operations which rely on context. 
2. Multiple checks are sent within a single BatchCheck operation for the same user/object/relation combination, each containing context.
3. The contexts between those checks differ in a specific way

### Fix
Upgrade to OpenFGA v1.14.0

### Acknowledgement
OpenFGA would like to thank @bugbunny-research for the discovery and detailed report.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-jwvj-g8pc-cx45
- https://nvd.nist.gov/vuln/detail/CVE-2026-34972
- https://github.com/openfga/openfga
