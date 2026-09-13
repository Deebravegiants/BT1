# [M] Weblate: Object-scoped RSS feeds disclose private change history to unauthorized users

## Summary
Severity: Medium
Advisory: CVE-2026-77507
Aliases: GHSA-vvc6-wvqm-w5gc
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-77507
Type: osv

## Details
Weblate is a web-based continuous localization platform used to manage software translations. In versions prior to 2026.8, Weblate's object-scoped RSS feeds do not apply the permission checks used elsewhere, allowing unauthorized users to read change-history metadata from private projects and restricted components. On installations that permit anonymous access, this metadata can be retrieved without any authentication. The exposed information can include project and component identities, contributor usernames and full names, action types, timestamps, and translation or unit links, though translated-string content is not included in the feed. Installations using private projects or restricted components are affected. This issue is fixed in version 2026.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77507.json
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-vvc6-wvqm-w5gc
- https://nvd.nist.gov/vuln/detail/CVE-2026-77507
- https://github.com/WeblateOrg/weblate/commit/9bcccfd3a38eea6ebffce582222cd5eac3aa3642
