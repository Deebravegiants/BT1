# [M] Exposure of messages in BigBlueButton public chats

## Summary
Severity: Medium
Advisory: CVE-2022-29232
Aliases: GHSA-3fqh-p4qr-vfm9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-06-01
Source: https://osv.dev/vulnerability/CVE-2022-29232
Type: osv

## Details
BigBlueButton is an open source web conferencing system. Starting with version 2.2 and prior to versions 2.3.9 and 2.4-beta-1, an attacker can circumvent access controls to obtain the content of public chat messages from different meetings on the server. The attacker must be a participant in a meeting on the server. BigBlueButton versions 2.3.9 and 2.4-beta-1 contain a patch for this issue. There are currently no known workarounds.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.3.9
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.4-beta-1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29232.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-3fqh-p4qr-vfm9
- https://nvd.nist.gov/vuln/detail/CVE-2022-29232
- https://github.com/bigbluebutton/bigbluebutton/pull/12861
