# [H] BigBlueButton API checksum bypass via presentationUploadExternalUrl

## Summary
Severity: High
Advisory: CVE-2026-46353
Aliases: GHSA-43hc-5g2m-cqff
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-46353
Type: osv

## Details
BigBlueButton is an open-source virtual classroom. Prior to 3.0.21, bbb-web checksum validation could be bypassed when a presentationUploadExternalUrl parameter was supplied to API request handling in CreateMeeting.java and ValidationService.java, allowing a user to send valid requests to some endpoints without a checksum. This issue is fixed in version 3.0.21.

## References
- https://github.com/bigbluebutton/bigbluebutton/releases/tag/v3.0.21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46353.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-43hc-5g2m-cqff
- https://nvd.nist.gov/vuln/detail/CVE-2026-46353
- https://github.com/bigbluebutton/bigbluebutton/commit/36fd1b407488a0c56ce620b91184d5a8aea68b3d
