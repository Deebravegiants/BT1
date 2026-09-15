# [H] BIT-modsecurity-2024-46292

## Summary
Severity: High
Advisory: BIT-modsecurity-2024-46292
Aliases: BIT-modsecurity2-2024-46292, CVE-2024-46292
Ecosystem: Bitnami
Published: 2025-06-18
Source: https://osv.dev/vulnerability/BIT-modsecurity-2024-46292
Type: osv

## Affected
- Bitnami: `modsecurity` — affected >=3.0.12 <3.0.13

## Details
A buffer overflow in modsecurity v3.0.12 allows attackers to cause a Denial of Service (DoS) via a crafted input inserted into the name parameter. NOTE: this is disputed by the Supplier because it cannot be reproduced. Also, the product's documentation indicates that it is not guaranteed to be usable with very large values of SecRequestBodyNoFilesLimit (which are required by the claimed issue).

## References
- https://github.com/owasp-modsecurity/ModSecurity/blob/v3/master/README.md
- https://github.com/yoloflz101/yoloflz/blob/main/README.md
- https://modsecurity.org/20241011/about-cve-2024-46292-2024-october/
- https://nvd.nist.gov/vuln/detail/CVE-2024-46292
