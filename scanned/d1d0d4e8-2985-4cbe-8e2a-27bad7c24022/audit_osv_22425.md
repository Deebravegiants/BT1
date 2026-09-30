# [M] Improper access control for breakout rooms in BigBlue Button

## Summary
Severity: Medium
Advisory: CVE-2022-29233
Aliases: GHSA-3mr9-p9gw-cf33
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-06-01
Source: https://osv.dev/vulnerability/CVE-2022-29233
Type: osv

## Details
BigBlueButton is an open source web conferencing system. In BigBlueButton starting with 2.2 but before 2.3.18 and 2.4-rc-1, an attacker can circumvent access controls to gain access to all breakout rooms of the meeting they are in. The permission checks rely on knowledge of internal ids rather than on verification of the role of the user. Versions 2.3.18 and 2.4-rc-1 contain a patch for this issue. There are currently no known workarounds.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.3.18
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.4-rc-1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29233.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-3mr9-p9gw-cf33
- https://nvd.nist.gov/vuln/detail/CVE-2022-29233
- https://github.com/bigbluebutton/bigbluebutton/pull/13117
- https://github.com/bigbluebutton/bigbluebutton/pull/14265
