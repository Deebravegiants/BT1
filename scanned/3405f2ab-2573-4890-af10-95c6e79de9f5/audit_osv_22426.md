# [M] Grace period for lock settings in public/private chats in BigBlueButton

## Summary
Severity: Medium
Advisory: CVE-2022-29234
Aliases: GHSA-36vc-c338-6xjv
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2022-06-01
Source: https://osv.dev/vulnerability/CVE-2022-29234
Type: osv

## Details
BigBlueButton is an open source web conferencing system. Starting in version 2.2 and prior to versions 2.3.18 and 2.4.1, an attacker could send messages to a locked chat within a grace period of 5s any lock setting in the meeting was changed. The attacker needs to be a participant in the meeting. Versions 2.3.18 and 2.4.1 contain a patch for this issue. There are currently no known workarounds.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.3.18
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.4.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29234.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-36vc-c338-6xjv
- https://nvd.nist.gov/vuln/detail/CVE-2022-29234
- https://github.com/bigbluebutton/bigbluebutton/pull/13850
- https://github.com/bigbluebutton/bigbluebutton/pull/14265
