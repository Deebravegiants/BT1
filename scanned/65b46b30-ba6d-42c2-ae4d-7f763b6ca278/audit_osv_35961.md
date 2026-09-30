# [M] Concrete CMS 9.2.0 to 9.5.2 Express REST API list endpoint exposes restricted Express entries via Missing Authorization

## Summary
Severity: Medium
Advisory: CVE-2026-18122
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-18122
Type: osv

## Details
Concrete CMS 9.2.0 to 9.5.2 Express REST API list endpoint exposes restricted Express entries via Missing Authorization; the Concrete CMS REST API's Express entry collection endpoint disabled the per-entry view permission check. An OAuth token with read scope for an Express entity could enumerate entries that its user context lacked permission to view, disclosing each entry's public identifier, URL, label, dates, and any attribute or associated-entry data requested via the includes parameter. The Concrete CMS security team gave this vulnerability a CVSS v4.0 score of 6.0 with vector CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N. Thanks riodrwn for reporting.

## References
- https://documentation.concretecms.org/developers/introduction/version-history/953-release-notes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18122.json
- https://github.com/concretecms/concretecms
- https://nvd.nist.gov/vuln/detail/CVE-2026-18122
