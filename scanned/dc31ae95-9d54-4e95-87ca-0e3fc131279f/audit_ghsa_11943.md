# [H] Netmaker has Insufficient Authorization in Host Token Verification

## Summary
Severity: High
Advisory: GHSA-hmqr-wjmj-376c
CVE: CVE-2026-29194
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-hmqr-wjmj-376c
Type: github-advisory

## Affected
- Go: `github.com/gravitl/netmaker` — affected >=0 <1.5.0

## Details
The Authorise middleware in Netmaker incorrectly validates host JWT tokens. When a route permits host authentication (hostAllowed=true), a valid host token bypasses all subsequent authorisation checks without verifying that the host is authorised to access the specific requested resource. Any entity possessing knowledge of object identifiers (node IDs, host IDs) can craft a request with an arbitrary valid host token to access, modify, or delete resources belonging to other hosts. Affected endpoints include node info retrieval, host deletion, MQTT signal transmission, fallback host updates, and failover operations.


> Credits
> Artem Danilov (Positive Technologies)

## References
- https://github.com/gravitl/netmaker/security/advisories/GHSA-hmqr-wjmj-376c
- https://nvd.nist.gov/vuln/detail/CVE-2026-29194
- https://github.com/gravitl/netmaker
- https://github.com/gravitl/netmaker/releases/tag/v1.5.0
