# [M] CVE-2019-19035

## Summary
Severity: Medium
Advisory: CVE-2019-19035
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-11-17
Source: https://osv.dev/vulnerability/CVE-2019-19035
Type: osv

## Details
jhead 3.03 is affected by: heap-based buffer over-read. The impact is: Denial of service. The component is: ReadJpegSections and process_SOFn in jpgfile.c. The attack vector is: Open a specially crafted JPEG file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GPNV43VBUCMUBRBKPJBY4DDSYLHQ2GFR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UOL6LCMEVOOB342EJ4TKWTPJAJPJSVWH/
- https://security.gentoo.org/glsa/202007-17
- https://bugzilla.redhat.com/show_bug.cgi?id=1765647
