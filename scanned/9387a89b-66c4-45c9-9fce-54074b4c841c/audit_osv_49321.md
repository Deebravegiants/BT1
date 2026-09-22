# [C] CVE-2019-1010174

## Summary
Severity: Critical
Advisory: CVE-2019-1010174
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-25
Source: https://osv.dev/vulnerability/CVE-2019-1010174
Type: osv

## Details
CImg The CImg Library v.2.3.3 and earlier is affected by: command injection. The impact is: RCE. The component is: load_network() function. The attack vector is: Loading an image from a user-controllable url can lead to command injection, because no string sanitization is done on the url. The fixed version is: v.2.3.4.

## References
- https://lists.debian.org/debian-lts-announce/2019/09/msg00030.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00033.html
- https://framagit.org/dtschump/CImg/commit/5ce7a426b77f814973e56182a0e76a2b04904146
