# [M] CVE-2022-37660

## Summary
Severity: Medium
Advisory: CVE-2022-37660
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-02-11
Source: https://osv.dev/vulnerability/CVE-2022-37660
Type: osv

## Details
In hostapd 2.10 and earlier, the PKEX code remains active even after a successful PKEX association. An attacker that successfully bootstrapped public keys with another entity using PKEX in the past, will be able to subvert a future bootstrapping by passively observing public keys, re-using the encrypting element Qi and subtracting it from the captured message M (X = M - Qi). This will result in the public ephemeral key X; the only element required to subvert the PKEX association.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-585531.html
- https://link.springer.com/article/10.1007/s10207-025-00988-3
- https://lists.debian.org/debian-lts-announce/2025/04/msg00019.html
- https://w1.fi/cgit/hostap/commit/?id=15af83cf1846870873a011ed4d714732f01cd2e4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37660.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-37660
