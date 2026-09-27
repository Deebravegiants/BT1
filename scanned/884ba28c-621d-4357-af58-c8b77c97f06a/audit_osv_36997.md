# [M] FOSSBilling: IDOR in Servicecustom Client API allows cross-client data access

## Summary
Severity: Medium
Advisory: CVE-2026-27708
Aliases: GHSA-p36w-9x66-488j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-27708
Type: osv

## Details
FOSSBilling is a free, open-source billing and client management system. In versions 0.7.2 and prior, the Servicecustom Client API's __call method accepts an order_id parameter and fetches the associated order without verifying the authenticated client owns it, potentially exposing cross-client data through IDOR. An authenticated client can access any other client's custom service by guessing sequential order IDs. This can lead to a confidentiality breach — attackers can read client PII (name, email, phone, address, company details, VAT number) and service configuration data belonging to other clients. This issue has been fixed in version 0.8.0.

## References
- https://github.com/FOSSBilling/FOSSBilling/releases/tag/0.8.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27708.json
- https://github.com/FOSSBilling/FOSSBilling/security/advisories/GHSA-p36w-9x66-488j
- https://nvd.nist.gov/vuln/detail/CVE-2026-27708
