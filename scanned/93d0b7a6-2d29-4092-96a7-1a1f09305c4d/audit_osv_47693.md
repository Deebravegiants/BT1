# [M] CVE-2017-1000122

## Summary
Severity: Medium
Advisory: CVE-2017-1000122
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2017-11-01
Source: https://osv.dev/vulnerability/CVE-2017-1000122
Type: osv

## Details
The UNIX IPC layer in WebKit, including WebKitGTK+ prior to 2.16.3, does not properly validate certain message metadata, allowing a compromised secondary process to cause a denial of service (release assertion) of the UI process. This vulnerability does not affect Apple products.

## References
- http://trac.webkit.org/changeset/217206
- https://webkitgtk.org/security/WSA-2017-0007.html
