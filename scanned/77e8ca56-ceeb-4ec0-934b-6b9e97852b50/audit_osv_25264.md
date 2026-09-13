# [M] Non-constant time HMAC comparison in Adyen plugin in Saleor

## Summary
Severity: Medium
Advisory: CVE-2023-32694
Aliases: GHSA-3rqj-9v87-2x3f
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-05-25
Source: https://osv.dev/vulnerability/CVE-2023-32694
Type: osv

## Details
Saleor Core is a composable, headless commerce API. Saleor's `validate_hmac_signature` function is vulnerable to timing attacks. Malicious users could abuse this vulnerability on Saleor deployments having the Adyen plugin enabled in order to determine the secret key and forge fake events, this could affect the database integrity such as marking an order as paid when it is not. This issue has been patched in versions 3.7.68, 3.8.40, 3.9.49, 3.10.36, 3.11.35, 3.12.25, and 3.13.16.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32694.json
- https://github.com/saleor/saleor/security/advisories/GHSA-3rqj-9v87-2x3f
- https://nvd.nist.gov/vuln/detail/CVE-2023-32694
- https://github.com/saleor/saleor/commit/1328274e1a3d04ab87d7daee90229ff47b3bc35e
