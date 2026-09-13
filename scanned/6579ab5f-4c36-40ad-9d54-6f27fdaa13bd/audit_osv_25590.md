# [H] Path traversal allows tricking the Talk Android app into writing files into it's root directory

## Summary
Severity: High
Advisory: CVE-2023-39957
Aliases: GHSA-36f7-93f3-mcfj
CVSS: 7.2 (CVSS:3.0/AV:L/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-08-10
Source: https://osv.dev/vulnerability/CVE-2023-39957
Type: osv

## Details
Nextcloud Talk Android allows users to place video and audio calls through Nextcloud on Android. Prior to version 17.0.0, an unprotected intend allowed malicious third party apps to trick the Talk Android app into writing files outside of its intended cache directory. Nextcloud Talk Android version 17.0.0 has a patch for this issue. No known workarounds are available.

## References
- https://hackerone.com/reports/1997029
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39957.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-36f7-93f3-mcfj
- https://nvd.nist.gov/vuln/detail/CVE-2023-39957
- https://github.com/nextcloud/talk-android/pull/3064
