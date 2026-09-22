# [M] Discourse-reactions' reaction data and public topic whisper content exposed on reactions given user activity page

## Summary
Severity: Medium
Advisory: CVE-2024-31219
Aliases: GHSA-7cqc-5xrw-xh67
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-04-15
Source: https://osv.dev/vulnerability/CVE-2024-31219
Type: osv

## Details
Discourse-reactions is a plugin that allows user to add their reactions to the post. When whispers are enabled on a site via `whispers_allowed_groups` and reactions are made on whispers on public topics, the contents of the whisper and the reaction data are shown on the `/u/:username/activity/reactions` endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31219.json
- https://github.com/discourse/discourse-reactions/security/advisories/GHSA-7cqc-5xrw-xh67
- https://nvd.nist.gov/vuln/detail/CVE-2024-31219
- https://github.com/discourse/discourse-reactions/commit/6a5a8dacd7e5cbbbbe7d2288b1df9c1062994dbe
