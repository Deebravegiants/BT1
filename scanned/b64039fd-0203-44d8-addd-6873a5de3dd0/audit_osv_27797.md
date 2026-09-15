# [M] Uninvited user is able to join and mark the attendance of the the private event

## Summary
Severity: Medium
Advisory: CVE-2024-26145
Aliases: GHSA-4hh7-6m34-p2jp
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2024-26145
Type: osv

## Details
Discourse Calendar adds the ability to create a dynamic calendar in the first post of a topic on Discourse. Uninvited users are able to gain access to private events by crafting a request to update their attendance. This problem is resolved in commit dfc4fa15f340189f177a1d1ab2cc94ffed3c1190. As a workaround, one may use post visibility to limit access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26145.json
- https://github.com/discourse/discourse-calendar/security/advisories/GHSA-4hh7-6m34-p2jp
- https://nvd.nist.gov/vuln/detail/CVE-2024-26145
- https://github.com/discourse/discourse-calendar/commit/dfc4fa15f340189f177a1d1ab2cc94ffed3c1190
