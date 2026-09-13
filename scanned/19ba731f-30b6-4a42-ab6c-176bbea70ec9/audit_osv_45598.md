# [M] aria2c accepts a server certificate with incorrect Extended Key Usage (EKU). If the attackers...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1347
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/JLSEC-2026-1347
Type: osv

## Affected
- Julia: `Aria2_jll` — affected >=0 <1.37.0+0

## Details
aria2c accepts a server certificate with incorrect Extended Key Usage (EKU). If the attackers compromise a certificate (with the associated private key) issued for a different purpose, they may be able to reuse it for TLS server authentication.

## References
- https://github.com/advisories/GHSA-rpx3-3f8j-f6v2
- https://nvd.nist.gov/vuln/detail/CVE-2026-8367
- https://www.tenable.com/security/research/tra-2026-38
