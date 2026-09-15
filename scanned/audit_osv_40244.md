# [M] URI nameConstraints not enforced in ConfirmNameConstraints()

## Summary
Severity: Medium
Advisory: CVE-2026-5263
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:L/VA:N/SC:H/SI:N/SA:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-5263
Type: osv

## Details
URI nameConstraints from constrained intermediate CAs are parsed but not enforced during certificate chain verification in wolfcrypt/src/asn.c. A compromised or malicious sub-CA could issue leaf certificates with URI SAN entries that violate the nameConstraints of the issuing CA, and wolfSSL would accept them as valid.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2410
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5263.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5263
- https://github.com/wolfSSL/wolfssl/pull/10048
- https://github.com/wolfSSL/wolfssl
