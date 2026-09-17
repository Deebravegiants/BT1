# [M] CVE-2020-25664

## Summary
Severity: Medium
Advisory: CVE-2020-25664
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2020-12-08
Source: https://osv.dev/vulnerability/CVE-2020-25664
Type: osv

## Details
In WriteOnePNGImage() of the PNG coder at coders/png.c, an improper call to AcquireVirtualMemory() and memset() allows for an out-of-bounds write later when PopShortPixel() from MagickCore/quantum-private.h is called. The patch fixes the calls by adding 256 to rowbytes. An attacker who is able to supply a specially crafted image could affect availability with a low impact to data integrity. This flaw affects ImageMagick versions prior to 6.9.10-68 and 7.0.8-68.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z3J6D7POCQYQKNVRDYLTTPM5SQC3WVTR/
- https://bugzilla.redhat.com/show_bug.cgi?id=1891605
