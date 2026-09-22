# [M] aria2c Improper Certificate Validation

## Summary
Severity: Medium
Advisory: CVE-2026-8367
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-8367
Type: osv

## Details
aria2c accepts a server certificate with incorrect Extended Key Usage (EKU). If the attackers compromise a certificate (with the associated private key) issued for a different purpose, they may be able to reuse it for TLS server authentication.

## References
- https://www.tenable.com/security/research/tra-2026-38
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8367.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8367
