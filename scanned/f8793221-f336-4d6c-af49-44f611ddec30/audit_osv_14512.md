# [H] CVE-2019-1010006

## Summary
Severity: High
Advisory: CVE-2019-1010006
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-15
Source: https://osv.dev/vulnerability/CVE-2019-1010006
Type: osv

## Details
Evince 3.26.0 is affected by buffer overflow. The impact is: DOS / Possible code execution. The component is: backend/tiff/tiff-document.c. The attack vector is: Victim must open a crafted PDF file. The issue occurs because of an incorrect integer overflow protection mechanism in tiff_document_render and tiff_document_get_thumbnail.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00046.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00013.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00014.html
- https://seclists.org/bugtraq/2020/Feb/18
- https://usn.ubuntu.com/4067-1/
- https://www.debian.org/security/2020/dsa-4624
- http://bugzilla.maptools.org/show_bug.cgi?id=2745
- https://bugzilla.gnome.org/show_bug.cgi?id=788980
