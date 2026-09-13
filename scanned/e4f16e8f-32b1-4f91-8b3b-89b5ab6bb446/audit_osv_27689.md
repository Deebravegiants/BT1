# [M] User can see invitees in events created in PMs and private categories

## Summary
Severity: Medium
Advisory: CVE-2024-24817
Aliases: GHSA-wwq5-g5cp-c69f
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2024-24817
Type: osv

## Details
Discourse Calendar adds the ability to create a dynamic calendar in the first post of a topic on the open-source discussion platform Discourse. Prior to version 0.4, event invitees created in topics in private categories or PMs (private messages) can be retrieved by anyone, even if they're not logged in. This problem is resolved in version 0.4 of the discourse-calendar plugin. While no known workaround is available, putting the site behind `login_required` will disallow this endpoint to be used by anonymous users, but logged in users can still get the list of invitees in the private topics.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24817.json
- https://github.com/discourse/discourse-calendar/security/advisories/GHSA-wwq5-g5cp-c69f
- https://nvd.nist.gov/vuln/detail/CVE-2024-24817
- https://github.com/discourse/discourse-calendar/commit/84ef46a38cf02748ecacad16c5d9c6fec12dc8da
