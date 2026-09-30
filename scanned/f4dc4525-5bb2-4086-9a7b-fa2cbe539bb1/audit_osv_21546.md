# [H] CVE-2021-43830

## Summary
Severity: High
Advisory: CVE-2021-43830
Aliases: GHSA-f565-3whr-6m96
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-14
Source: https://osv.dev/vulnerability/CVE-2021-43830
Type: osv

## Details
OpenProject is a web-based project management software. OpenProject versions >= 12.0.0 are vulnerable to a SQL injection in the budgets module. For authenticated users with the "Edit budgets" permission, the request to reassign work packages to another budget unsufficiently sanitizes user input in the `reassign_to_id` parameter. The vulnerability has been fixed in version 12.0.4. Versions prior to 12.0.0 are not affected. If you're upgrading from an older version, ensure you are upgrading to at least version 12.0.4. If you are unable to upgrade in a timely fashion, the following patch can be applied: https://github.com/opf/openproject/pull/9983.patch

## References
- https://github.com/opf/openproject/releases/tag/v12.0.4
- https://github.com/opf/openproject/security/advisories/GHSA-f565-3whr-6m96
- https://github.com/opf/openproject/pull/9983
- https://github.com/opf/openproject/pull/9983.patch
