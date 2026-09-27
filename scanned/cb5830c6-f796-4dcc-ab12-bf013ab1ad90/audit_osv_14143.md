# [H] CVE-2018-7441

## Summary
Severity: High
Advisory: CVE-2018-7441
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7441
Type: osv

## Details
Leptonica through 1.75.3 uses hardcoded /tmp pathnames, which might allow local users to overwrite arbitrary files or have unspecified other impact by creating files in advance or winning a race condition, as demonstrated by /tmp/junk_split_image.ps in prog/splitimage2pdf.c.

## References
- https://lists.debian.org/debian-lts/2018/02/msg00054.html
- https://security.gentoo.org/glsa/202312-01
