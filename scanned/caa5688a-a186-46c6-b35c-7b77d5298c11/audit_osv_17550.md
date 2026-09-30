# [C] CVE-2020-16163

## Summary
Severity: Critical
Advisory: CVE-2020-16163
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-07-30
Source: https://osv.dev/vulnerability/CVE-2020-16163
Type: osv

## Details
An issue was discovered in RIPE NCC RPKI Validator 3.x before 3.1-2020.07.06.14.28. RRDP fetches proceed even with a lack of validation of a TLS HTTPS endpoint. This allows remote attackers to bypass intended access restrictions, or to trigger denial of service to traffic directed to co-dependent routing systems. NOTE: third parties assert that the behavior is intentionally permitted by RFC 8182

## References
- https://github.com/RIPE-NCC/rpki-validator-3/issues/159
