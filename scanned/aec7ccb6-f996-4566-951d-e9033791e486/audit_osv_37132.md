# [M] elabftw has entry title leakage through autocompletion search

## Summary
Severity: Medium
Advisory: CVE-2026-28511
Aliases: GHSA-wm4r-p2jg-2mj3
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-28511
Type: osv

## Details
eLabFTW is an open source electronic lab notebook. Prior to version 5.4.2, in certain cases, an authenticated user performing a numeric reference/search can return results that include resources the requesting user is not authorized to view. The exposed information is limited (only the title). Attempts to access the underlying protected resource content remain blocked by authorization checks. Version 5.4.2 fixes the issue.

# Affected Scope

Cross-scope visibility of titles.
No confirmed bypass of content-level access controls

# Preconditions

An authenticated user account

No special privileges required beyond standard access

# Impact

This may enable unauthorized disclosure of sensitive information if confidential data is included in resource titles. Examples could include project names, patient identifiers, or other regulated information embedded in titles.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28511.json
- https://github.com/elabftw/elabftw/security/advisories/GHSA-wm4r-p2jg-2mj3
- https://nvd.nist.gov/vuln/detail/CVE-2026-28511
