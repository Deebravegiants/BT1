# [C] Frappe account takeover via password reset token leakage

## Summary
Severity: Critical
Advisory: CVE-2025-52898
Aliases: GHSA-p284-r7rh-wq7j
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-06-30
Source: https://osv.dev/vulnerability/CVE-2025-52898
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to versions 14.94.3 and 15.58.0, a carefully crafted request could lead to a malicious actor getting access to a user's password reset token. This can only be exploited on self hosted instances configured in a certain way. Frappe Cloud users are safe. This issue has been patched in versions 14.94.3 and 15.58.0. Workarounds for this issue involve verifying password reset URLs before clicking on them or upgrading for self hosted users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52898.json
- https://github.com/frappe/frappe/security/advisories/GHSA-p284-r7rh-wq7j
- https://nvd.nist.gov/vuln/detail/CVE-2025-52898
- https://github.com/frappe/frappe/commit/52e31337a6c964189c8b883a2f7bc3a28ab374f2
- https://github.com/frappe/frappe/commit/5b4849b1ab5fd796b306312745b4e202b0e90d66
- https://github.com/frappe/frappe/pull/31522
