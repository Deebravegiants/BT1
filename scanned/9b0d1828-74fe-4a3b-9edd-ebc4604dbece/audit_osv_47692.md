# [C] CVE-2017-1000121

## Summary
Severity: Critical
Advisory: CVE-2017-1000121
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-01
Source: https://osv.dev/vulnerability/CVE-2017-1000121
Type: osv

## Details
The UNIX IPC layer in WebKit, including WebKitGTK+ prior to 2.16.3, does not properly validate message size metadata, allowing a compromised secondary process to trigger an integer overflow and subsequent buffer overflow in the UI process. This vulnerability does not affect Apple products.

## References
- https://webkitgtk.org/security/WSA-2017-0007.html
- http://trac.webkit.org/changeset/217126/webkit
