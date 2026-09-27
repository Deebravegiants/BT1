# [M] BigBlueButton subject to Ineffective user bans

## Summary
Severity: Medium
Advisory: CVE-2022-41961
Aliases: GHSA-wxjp-h88g-7fqg
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2022-12-16
Source: https://osv.dev/vulnerability/CVE-2022-41961
Type: osv

## Details
BigBlueButton is an open source web conferencing system. Versions prior to 2.4-rc-6 are subject to Ineffective user bans. The attacker could register multiple users, and join the meeting with one of them. When that user is banned, they could still join the meeting with the remaining registered users from the same extId. This issue has been fixed by improving permissions such that banning a user removes all users related to their extId, including registered users that have not joined the meeting. This issue is patched in versions 2.4-rc-6 and 2.5-alpha-1. There are no workarounds.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.4-rc-6
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.5-alpha-1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41961.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-wxjp-h88g-7fqg
- https://nvd.nist.gov/vuln/detail/CVE-2022-41961
