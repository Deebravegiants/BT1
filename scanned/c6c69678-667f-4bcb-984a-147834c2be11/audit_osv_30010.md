# [M] CVE-2024-48948

## Summary
Severity: Medium
Advisory: CVE-2024-48948
Aliases: GHSA-fc9h-whq2-v747
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-10-15
Source: https://osv.dev/vulnerability/CVE-2024-48948
Type: osv

## Details
The Elliptic package 6.5.7 for Node.js, in its for ECDSA implementation, does not correctly verify valid signatures if the hash contains at least four leading 0 bytes and when the order of the elliptic curve's base point is smaller than the hash, because of an _truncateToN anomaly. This leads to valid signatures being rejected. Legitimate transactions or communications may be incorrectly flagged as invalid.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48948.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48948
- https://security.netapp.com/advisory/ntap-20241220-0004/
- https://github.com/indutny/elliptic/issues/321
- https://github.com/indutny/elliptic/pull/322
- https://blog.trailofbits.com/2025/11/18/we-found-cryptography-bugs-in-the-elliptic-library-using-wycheproof/
