# [M] Improper access control to polling votes

## Summary
Severity: Medium
Advisory: CVE-2022-23490
Aliases: GHSA-4qgc-xhw5-6qfg
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-12-16
Source: https://osv.dev/vulnerability/CVE-2022-23490
Type: osv

## Details
BigBlueButton is an open source web conferencing system. Versions prior to 2.4.0 expose sensitive information to Unauthorized Actors. This issue affects meetings with polls, where the attacker is a meeting participant. Subscribing to the current-poll collection does not update the client UI, but does give the attacker access to the contents of the collection, which include the individual poll responses. This issue is patched in version 2.4.0. There are no workarounds.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v2.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23490.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-4qgc-xhw5-6qfg
- https://nvd.nist.gov/vuln/detail/CVE-2022-23490
