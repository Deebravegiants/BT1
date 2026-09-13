# [M] CVE-2014-9983

## Summary
Severity: Medium
Advisory: CVE-2014-9983
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2017-06-04
Source: https://osv.dev/vulnerability/CVE-2014-9983
Type: osv

## Details
Directory Traversal exists in RAR 4.x and 5.x because an unpack operation follows any symlinks, including symlinks contained in the archive. This allows remote attackers to write to arbitrary files via a crafted archive.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=774172
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=774172
