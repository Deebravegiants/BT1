# [C] CVE-2021-21245

## Summary
Severity: Critical
Advisory: CVE-2021-21245
Aliases: GHSA-62m2-38q5-96w9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-15
Source: https://osv.dev/vulnerability/CVE-2021-21245
Type: osv

## Details
OneDev is an all-in-one devops platform. In OneDev before version 4.0.3, AttachmentUploadServlet also saves user controlled data (`request.getInputStream()`) to a user specified location (`request.getHeader("File-Name")`). This issue may lead to arbitrary file upload which can be used to upload a WebShell to OneDev server. This issue is addressed in 4.0.3 by only allowing uploaded file to be in attachments folder. The webshell issue is not possible as OneDev never executes files in attachments folder.

## References
- https://github.com/theonedev/onedev/security/advisories/GHSA-62m2-38q5-96w9
- https://github.com/theonedev/onedev/commit/0c060153fb97c0288a1917efdb17cc426934dacb
