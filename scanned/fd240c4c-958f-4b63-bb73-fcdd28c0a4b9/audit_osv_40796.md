# [M] BigBlueButton: IDOR on BBB through /api/graphql via POST parameter "presentationId" leads to Authentication Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-55489
Aliases: GHSA-jxpq-r3h3-p75g
CVSS: 4.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:L/A:L)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-55489
Type: osv

## Details
BigBlueButton is an open-source virtual classroom. Prior to 3.0.29, BigBlueButton presenters could submit a presentationId through /api/graphql that identified a presentation belonging to another meeting. akka-bbb-apps/src/main/scala/org/bigbluebutton/core/apps/presentationpod/RemovePresentationPubMsgHdlr.scala did not verify the presentation's meeting identifier before deletion, allowing a presenter who knew the identifier to delete another meeting's presentation and disrupt its availability. This issue is fixed in version 3.0.29.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v3.0.29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55489.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-jxpq-r3h3-p75g
- https://nvd.nist.gov/vuln/detail/CVE-2026-55489
- https://github.com/bigbluebutton/bigbluebutton/commit/c9e93f9af07b9661e286d101b83cbccb891c551f
