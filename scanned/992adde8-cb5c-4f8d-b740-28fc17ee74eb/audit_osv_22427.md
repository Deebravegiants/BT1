# [M] Limited data exposure for shared external videos in BigBlueButton

## Summary
Severity: Medium
Advisory: CVE-2022-29235
Aliases: GHSA-x82p-j22f-v4q6
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-06-01
Source: https://osv.dev/vulnerability/CVE-2022-29235
Type: osv

## Details
BigBlueButton is an open source web conferencing system. Starting in version 2.2 and prior to versions 2.3.18 and 2.4-rc-6, an attacker who is able to obtain the meeting identifier for a meeting on a server can find information related to an external video being shared, like the current timestamp and play/pause. The problem has been patched in versions 2.3.18 and 2.4-rc-6 by modifying the stream to send the data only for users in the meeting. There are currently no known workarounds.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.3.18
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.4-rc-6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29235.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-x82p-j22f-v4q6
- https://nvd.nist.gov/vuln/detail/CVE-2022-29235
- https://github.com/bigbluebutton/bigbluebutton/pull/13788
- https://github.com/bigbluebutton/bigbluebutton/pull/14265
