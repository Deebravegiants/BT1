# [M] CtrlPanel has Missing Authentication Checks in Datatable Admin Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-34233
Aliases: GHSA-mj5g-j7fq-7hc4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-34233
Type: osv

## Details
CtrlPanel is open-source billing software for hosting providers. In versions 1.1.1 and prior, multiple admin controllers expose DataTable endpoints without authorization checks, allowing any authenticated user to access sensitive administrative data that should be restricted to administrators only. The affected admin controllers define datatable() methods that are reachable via GET requests but lack any permission or role verification. Because the routes fall under the /admin/ prefix, operators may assume they are protected - however, the middleware applied to this route group does not enforce admin-level authorization on these specific endpoints. As a result, any authenticated user (regardless of role) can query these endpoints and receive paginated JSON responses containing sensitive records. Exploitation can result in enumeration of user PII, payment and transaction records, active voucher and coupon codes, role and permission structure, server ownership mappings and support ticket contents. This issue has been fixed in version 1.2.0.

## References
- https://github.com/Ctrlpanel-gg/panel/releases/tag/1.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34233.json
- https://github.com/Ctrlpanel-gg/panel/security/advisories/GHSA-mj5g-j7fq-7hc4
- https://nvd.nist.gov/vuln/detail/CVE-2026-34233
