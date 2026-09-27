# [H] IDURAR has a Path Traversal (unauthenticated user can read sensitive data)

## Summary
Severity: High
Advisory: CVE-2024-47769
Aliases: GHSA-948g-2vm7-mfv7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-04
Source: https://osv.dev/vulnerability/CVE-2024-47769
Type: osv

## Details
IDURAR is open source ERP CRM accounting invoicing software. The vulnerability exists in the corePublicRouter.js file. Using the reference usage here, it is identified that the public endpoint is accessible to an unauthenticated user. The user's input is directly appended to the join statement without additional checks. This allows an attacker to send URL encoded malicious payload. The directory structure can be escaped to read system files by adding an encoded string (payload) at subpath location.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47769.json
- https://github.com/idurar/idurar-erp-crm/security/advisories/GHSA-948g-2vm7-mfv7
- https://nvd.nist.gov/vuln/detail/CVE-2024-47769
- https://github.com/idurar/idurar-erp-crm/commit/949bc6fe31f3175c9e1864d30cf6c8110179ac14
