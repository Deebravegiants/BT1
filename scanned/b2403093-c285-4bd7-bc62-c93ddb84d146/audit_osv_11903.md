# [H] CVE-2018-1000041

## Summary
Severity: High
Advisory: CVE-2018-1000041
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-1000041
Type: osv

## Details
GNOME librsvg version before commit c6ddf2ed4d768fd88adbea2b63f575cd523022ea contains a Improper input validation vulnerability in rsvg-io.c that can result in the victim's Windows username and NTLM password hash being leaked to remote attackers through SMB. This attack appear to be exploitable via The victim must process a specially crafted SVG file containing an UNC path on Windows.

## References
- https://github.com/GNOME/librsvg/commit/c6ddf2ed4d768fd88adbea2b63f575cd523022ea
- https://github.com/ImageMagick/librsvg/commit/f9d69eadd2b16b00d1a1f9f286122123f8e547dd
- https://lists.debian.org/debian-lts-announce/2018/02/msg00013.html
