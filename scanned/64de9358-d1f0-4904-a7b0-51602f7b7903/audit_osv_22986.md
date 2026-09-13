# [M] Discourse-calendar exposes members of hidden groups

## Summary
Severity: Medium
Advisory: CVE-2022-41913
Aliases: GHSA-jh96-w279-g7r9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-11-14
Source: https://osv.dev/vulnerability/CVE-2022-41913
Type: osv

## Details
Discourse-calendar is a plugin for the Discourse messaging platform which adds the ability to create a dynamic calendar in the first post of a topic. Members of private groups or public groups with private members can be listed by users, who can create and edit post events. This vulnerability only affects sites which have discourse post events enabled. This issue has been patched in commit `ca5ae3e7e` which will be included in future releases. Users unable to upgrade should disable the `discourse_post_event_enabled` setting to fully mitigate the issue. Also, it's possible to prevent regular users from using this vulnerability by removing all groups from the `discourse_post_event_allowed_on_groups` but note that moderators will still be able to use it.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41913.json
- https://github.com/discourse/discourse-calendar/security/advisories/GHSA-jh96-w279-g7r9
- https://nvd.nist.gov/vuln/detail/CVE-2022-41913
- https://github.com/discourse/discourse-calendar/commit/ca5ae3e7e0c2b32af5ca4ec69c95e95b2ecef2e9
