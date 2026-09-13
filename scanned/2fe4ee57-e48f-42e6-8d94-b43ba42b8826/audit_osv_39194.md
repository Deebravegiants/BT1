# [M] ERPNext: Possible SSRF by any authenticated user

## Summary
Severity: Medium
Advisory: CVE-2026-44441
Aliases: GHSA-m4m4-j2m2-7fcw
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-44441
Type: osv

## Details
ERPNext is a free and open source Enterprise Resource Planning tool. Prior to 15.106.0 and 16.16.0, a malicious user could send a crafted request to an endpoint, which would lead to the server making an HTTP call to a service of the user's choice. This vulnerability is fixed in 15.106.0 and 16.16.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44441.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-m4m4-j2m2-7fcw
- https://nvd.nist.gov/vuln/detail/CVE-2026-44441
