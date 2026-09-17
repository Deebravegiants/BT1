# [M] CVE-2017-18199

## Summary
Severity: Medium
Advisory: CVE-2017-18199
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-24
Source: https://osv.dev/vulnerability/CVE-2017-18199
Type: osv

## Details
realloc_symlink in rock.c in GNU libcdio before 1.0.0 allows remote attackers to cause a denial of service (NULL Pointer Dereference) via a crafted iso file.

## References
- http://ftp.gnu.org/gnu/libcdio/libcdio-1.0.0.tar.gz
- http://www.securityfocus.com/bid/103202
- https://access.redhat.com/errata/RHSA-2018:3246
- https://savannah.gnu.org/bugs/?52264
