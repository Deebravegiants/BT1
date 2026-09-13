# [M] Improper access control for pencil annotations in BigBlueButton

## Summary
Severity: Medium
Advisory: CVE-2022-29236
Aliases: GHSA-p93g-r9gm-9v6r
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-06-01
Source: https://osv.dev/vulnerability/CVE-2022-29236
Type: osv

## Details
BigBlueButton is an open source web conferencing system. Starting in version 2.2 and prior to versions 2.3.18 and 2.4-rc-6, an attacker can circumvent access restrictions for drawing on the whiteboard. The permission check is inadvertently skipped on the server, due to a previously introduced grace period. The attacker must be a meeting participant. The problem has been patched in versions 2.3.18 and 2.4-rc-6. There are currently no known workarounds.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.3.18
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.4-rc-6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29236.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-p93g-r9gm-9v6r
- https://nvd.nist.gov/vuln/detail/CVE-2022-29236
- https://github.com/bigbluebutton/bigbluebutton/pull/13803
- https://github.com/bigbluebutton/bigbluebutton/pull/14265
