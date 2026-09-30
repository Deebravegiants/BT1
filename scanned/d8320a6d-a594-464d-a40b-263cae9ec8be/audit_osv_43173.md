# [H] OpenSignLabs opensignserver - Authentication Bypass

## Summary
Severity: High
Advisory: CVE-2026-72691
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72691
Type: osv

## Details
An authentication bypass vulnerability in OpenSignLabs opensignserver through 2.37.0 allows an unauthenticated remote attacker to mint MASTER_KEY-signed file access tokens for arbitrary stored files via the getsignedurl Parse cloud function. The function skips its isAuthenticated check whenever any docId parameter is supplied, even one corresponding to no real document, allowing the authentication gate to be bypassed by supplying an arbitrary string as docId.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72691.json
- https://github.com/OpenSignLabs/OpenSign
- https://nvd.nist.gov/vuln/detail/CVE-2026-72691
