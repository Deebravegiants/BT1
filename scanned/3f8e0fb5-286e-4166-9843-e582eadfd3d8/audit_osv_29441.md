# [M] CVE-2024-42460

## Summary
Severity: Medium
Advisory: CVE-2024-42460
Aliases: GHSA-977x-g7h5-7qgw
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-08-02
Source: https://osv.dev/vulnerability/CVE-2024-42460
Type: osv

## Details
In the Elliptic package 6.5.6 for Node.js, ECDSA signature malleability occurs because there is a missing check for whether the leading bit of r and s is zero.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42460.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42460
- https://security.netapp.com/advisory/ntap-20241004-0005/
- https://github.com/indutny/elliptic/pull/317
