# [M] BigBlueButton Unrestricted File Upload vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-42803
Aliases: GHSA-w98f-6x8w-xhjc
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-30
Source: https://osv.dev/vulnerability/CVE-2023-42803
Type: osv

## Details
BigBlueButton is an open-source virtual classroom. BigBlueButton prior to version 2.6.0-beta.2 is vulnerable to unrestricted file upload, where the insertDocument API call does not validate the given file extension before saving the file, and does not remove it in case of validation failures. BigBlueButton 2.6.0-beta.2 contains a patch. There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42803.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-w98f-6x8w-xhjc
- https://nvd.nist.gov/vuln/detail/CVE-2023-42803
- https://github.com/bigbluebutton/bigbluebutton/pull/15990
