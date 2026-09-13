# [M] iPAddress name constraints not enforced when WOLFSSL_IP_ALT_NAME is undefined

## Summary
Severity: Medium
Advisory: CVE-2026-7532
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-7532
Type: osv

## Details
iPAddress name constraints bypass when WOLFSSL_IP_ALT_NAME is not defined. IP address name constraints are not enforced in that configuration, allowing a certificate to bypass an issuing CA's IP address constraints.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2409
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7532.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-7532
- https://github.com/wolfSSL/wolfssl/pull/10354
- https://github.com/wolfSSL/wolfssl
