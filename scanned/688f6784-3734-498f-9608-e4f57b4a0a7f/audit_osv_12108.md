# [M] CVE-2018-10289

## Summary
Severity: Medium
Advisory: CVE-2018-10289
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-22
Source: https://osv.dev/vulnerability/CVE-2018-10289
Type: osv

## Details
In MuPDF 1.13.0, there is an infinite loop in the fz_skip_space function of the pdf/pdf-xref.c file. A remote adversary could leverage this vulnerability to cause a denial of service via a crafted pdf file.

## References
- http://www.ghostscript.com/cgi-bin/findgit.cgi?2e43685dc8a8a886fc9df9b3663cf199404f7637
- https://lists.debian.org/debian-lts-announce/2021/09/msg00013.html
- https://bugs.ghostscript.com/show_bug.cgi?id=699271
