# [M] CVE-2023-33251

## Summary
Severity: Medium
Advisory: CVE-2023-33251
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-05-21
Source: https://osv.dev/vulnerability/CVE-2023-33251
Type: osv

## Details
When Akka HTTP before 10.5.2 accepts file uploads via the FileUploadDirectives.fileUploadAll directive, the temporary file it creates has too weak permissions: it is readable by other users on Linux or UNIX, a similar issue to CVE-2022-41946.

## References
- https://doc.akka.io/reference/security-announcements/akka-http-cve-2023-05-15.html
- https://akka.io/security/akka-http-cve-2023-05-15.html
