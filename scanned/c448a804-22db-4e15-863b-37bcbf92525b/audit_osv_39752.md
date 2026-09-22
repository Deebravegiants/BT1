# [H] OpenProject: Journal diff endpoint bypasses object, journal, and field visibility checks

## Summary
Severity: High
Advisory: CVE-2026-47193
Aliases: GHSA-f2rx-x2qj-2hgj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-47193
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.3.3 and 17.4.1, the journal diff endpoint discloses hidden historical field values without enforcing object and field visibility. This vulnerability is fixed in 17.3.3 and 17.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47193.json
- https://github.com/opf/openproject/security/advisories/GHSA-f2rx-x2qj-2hgj
- https://nvd.nist.gov/vuln/detail/CVE-2026-47193
