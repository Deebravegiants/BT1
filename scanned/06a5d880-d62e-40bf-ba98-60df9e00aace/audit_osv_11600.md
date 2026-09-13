# [C] CVE-2017-9031

## Summary
Severity: Critical
Advisory: CVE-2017-9031
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-17
Source: https://osv.dev/vulnerability/CVE-2017-9031
Type: osv

## Details
The WebUI component in Deluge before 1.3.15 contains a directory traversal vulnerability involving a request in which the name of the render file is not associated with any template file.

## References
- http://www.securityfocus.com/bid/99099
- http://dev.deluge-torrent.org/wiki/ReleaseNotes/1.3.15
- http://www.debian.org/security/2017/dsa-3856
- http://git.deluge-torrent.org/deluge/commit/?h=1.3-stable&id=41acade01ae88f7b7bbdba308a0886771aa582fd
- https://bugs.debian.org/862611
