# [M] OpenProject has Cross-Project Meeting Agenda Item Injection via Unscoped Section Lookup

## Summary
Severity: Medium
Advisory: CVE-2026-40896
Aliases: GHSA-hh5p-gwf8-h245
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-40896
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to version 17.3.0, a user with `manage_agendas` permission in any project can inject agenda items into meetings belonging to any other project on the instance — even projects they have no access to. No knowledge of the target project, meeting, or victim is required; the attacker can blindly spray items into every meeting on the instance by iterating sequential section IDs. Version 17.3.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40896.json
- https://github.com/opf/openproject/security/advisories/GHSA-hh5p-gwf8-h245
- https://nvd.nist.gov/vuln/detail/CVE-2026-40896
- https://github.com/opf/openproject/commit/8f693a1f35d0a84bb69af78fb6925f74329ae4fe
