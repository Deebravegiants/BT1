# [M] CVE-2021-40109

## Summary
Severity: Medium
Advisory: CVE-2021-40109
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2021-09-27
Source: https://osv.dev/vulnerability/CVE-2021-40109
Type: osv

## Details
A SSRF issue was discovered in Concrete CMS through 8.5.5. Users can access forbidden files on their local network. A user with permissions to upload files from external sites can upload a URL that redirects to an internal resource of any file type. The redirect is followed and loads the contents of the file from the redirected-to server. Files of disallowed types can be uploaded.

## References
- https://documentation.concretecms.org/developers/introduction/version-history/856-release-notes
- https://hackerone.com/reports/1102105
