# [H] CVE-2017-18198

## Summary
Severity: High
Advisory: CVE-2017-18198
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-24
Source: https://osv.dev/vulnerability/CVE-2017-18198
Type: osv

## Details
print_iso9660_recurse in iso-info.c in GNU libcdio before 1.0.0 allows remote attackers to cause a denial of service (heap-based buffer over-read) or possibly have unspecified other impact via a crafted iso file.

## References
- http://ftp.gnu.org/gnu/libcdio/libcdio-1.0.0.tar.gz
- http://www.securityfocus.com/bid/103200
- https://access.redhat.com/errata/RHSA-2018:3246
- https://savannah.gnu.org/bugs/?52265
