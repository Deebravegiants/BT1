# [M] CVE-2025-65502

## Summary
Severity: Medium
Advisory: CVE-2025-65502
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-65502
Type: osv

## Details
Null pointer dereference in add_ca_certs() in Cesanta Mongoose before 7.2 allows remote attackers to cause a denial of service via TLS initialization where SSL_CTX_get_cert_store() returns NULL.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65502.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65502
- https://github.com/cesanta/mongoose/issues/3306
- https://github.com/cesanta/mongoose/pull/3307
