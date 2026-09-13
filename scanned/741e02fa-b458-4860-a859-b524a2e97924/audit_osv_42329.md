# [C] MongoDB C Driver Cyrus SASL Canonicalization Buffer Overflow

## Summary
Severity: Critical
Advisory: CVE-2026-6691
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-6691
Type: osv

## Details
The MongoDB C Driver's Cyrus SASL integration performs unsafe string copying during username canonicalization, enabling a heap buffer overflow before any authentication or network traffic. This may be triggered by passing untrusted input in the username of a MongoDB URI with authMechanism=GSSAPI.

## References
- https://jira.mongodb.org/browse/CDRIVER-6134
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6691.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6691
