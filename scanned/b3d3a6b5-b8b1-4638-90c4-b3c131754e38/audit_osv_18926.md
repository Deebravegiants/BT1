# [H] CVE-2020-4079

## Summary
Severity: High
Advisory: CVE-2020-4079
Aliases: GHSA-vcv9-xp3j-7jwh
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2021-01-12
Source: https://osv.dev/vulnerability/CVE-2020-4079
Type: osv

## Details
Combodo iTop is a web based IT Service Management tool. In iTop before versions 2.7.2 and 2.8.0, when the ajax endpoint for the "excel export" portal functionality is called directly it allows getting data without scope filtering. This allows a user to access data they which they should not have access to. This is fixed in versions 2.7.2 and 3.0.0.

## References
- https://github.com/Combodo/iTop/security/advisories/GHSA-vcv9-xp3j-7jwh
