# [M] Frappe: Possible SSRF by any authenticated user

## Summary
Severity: Medium
Advisory: CVE-2026-31878
Aliases: GHSA-mggg-hmjm-j6c2
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31878
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to 14.100.1, 15.100.0, and 16.6.0, a malicious user could send a crafted request to an endpoint which would lead to the server making an HTTP call to a service of the user's choice. This vulnerability is fixed in 14.100.1, 15.100.0, and 16.6.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31878.json
- https://github.com/frappe/frappe/security/advisories/GHSA-mggg-hmjm-j6c2
- https://nvd.nist.gov/vuln/detail/CVE-2026-31878
