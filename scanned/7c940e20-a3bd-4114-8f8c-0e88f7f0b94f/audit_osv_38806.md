# [M] FOSSBilling has an unauthenticated payment bypass via IPN callback forgery

## Summary
Severity: Medium
Advisory: CVE-2026-42341
Aliases: GHSA-5493-9m76-2qrr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-42341
Type: osv

## Details
FOSSBilling is a free, open-source billing and client management system. Versions 0.6.0 through 0.7.2 have an unauthenticated payment bypass vulnerability in FOSSBilling's IPN callback endpoint. When the Custom payment adapter is enabled, an attacker can mark any unpaid invoice as paid and credit the associated client account without making an actual payment, by sending a single crafted HTTP request. Version 0.8.0 patches the issue. Some workarounds are available. Disable the Custom payment gateway if not actively needed and/or restrict access to `/ipn.php` at the web server level (e.g., via IP allowlisting), noting that this may interfere with legitimate payment callback processing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42341.json
- https://github.com/FOSSBilling/FOSSBilling/security/advisories/GHSA-5493-9m76-2qrr
- https://nvd.nist.gov/vuln/detail/CVE-2026-42341
