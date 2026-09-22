# [M] Weblate Has Uncontrolled Resource Consumption via

## Summary
Severity: Medium
Advisory: CVE-2026-62326
Aliases: GHSA-r52j-4vjp-q949
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-62326
Type: osv

## Details
Weblate is a web-based continuous localization platform used to manage software translations. In versions prior to 2026.7, a user with the built-in "Edit source" role can store a malicious regular expression in a source string's flags that is executed without any timeout, allowing them to stall requests and deny service. Regular expressions supplied through the regex: quality check and regex placeholders are compiled during validation but later run against translation content in RegexCheck and PlaceholderCheck with no time limit, so a catastrophic-backtracking pattern like ^(a|aa)+$ can consume CPU indefinitely. Because Weblate re-runs these checks for every linked target unit in the same request when a source unit's flags change, a single edit can trigger sustained CPU-bound denial of service. This issue is fixed in version 2026.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62326.json
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-r52j-4vjp-q949
- https://nvd.nist.gov/vuln/detail/CVE-2026-62326
- https://github.com/WeblateOrg/weblate/commit/8fd8431414bec5c86dbc94815319fc474518286a
