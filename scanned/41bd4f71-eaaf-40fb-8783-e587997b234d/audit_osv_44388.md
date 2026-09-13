# [H] Flowintel Organization Administrator Can Reset Full Administrator Password and Escalate Privileges

## Summary
Severity: High
Advisory: CVE-2026-81818
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81818
Type: osv

## Details
Affected versions of Flowintel contain an authorization flaw in the administrative user-edit API.


The existing authorization check correctly prevented an organization administrator from editing users in another organization, but it did not prevent them from editing a full administrator within their own organization. As a result, an org admin could modify that full administrator account, including changing its password. The upstream commit explicitly describes the issue as:


“Org admin can change the password of a full admin in the same organization.”


The fix adds a higher-privilege boundary check:


if user_to_edit.is_admin(): return ... 403

so organization administrators can no longer modify full administrator accounts.

Version impacted >=3.3.0

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81818.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81818
- https://github.com/flowintel/flowintel/commit/ffe64d1133b7d84909a69661bd5fee607e9ce757.patch
- https://github.com/flowintel/flowintel
