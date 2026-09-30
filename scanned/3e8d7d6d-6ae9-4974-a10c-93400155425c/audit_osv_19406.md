# [C] CVE-2021-21242

## Summary
Severity: Critical
Advisory: CVE-2021-21242
Aliases: GHSA-5q3q-f373-2jv8
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-15
Source: https://osv.dev/vulnerability/CVE-2021-21242
Type: osv

## Details
OneDev is an all-in-one devops platform. In OneDev before version 4.0.3, there is a critical vulnerability which can lead to pre-auth remote code execution. AttachmentUploadServlet deserializes untrusted data from the `Attachment-Support` header. This Servlet does not enforce any authentication or authorization checks. This issue may lead to pre-auth remote code execution. This issue was fixed in 4.0.3 by removing AttachmentUploadServlet and not using deserialization

## References
- https://github.com/theonedev/onedev/security/advisories/GHSA-5q3q-f373-2jv8
- https://github.com/theonedev/onedev/commit/f864053176c08f59ef2d97fea192ceca46a4d9be
