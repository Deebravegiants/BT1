# [H] CVE-2018-7437

## Summary
Severity: High
Advisory: CVE-2018-7437
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7437
Type: osv

## Details
An issue was discovered in FreeXL before 1.0.5. There is a heap-based buffer over-read in a memcpy call of the parse_SST function.

## References
- https://groups.google.com/forum/#%21topic/spatialite-users/b-d9iB5TDPE
- https://lists.debian.org/debian-lts-announce/2018/03/msg00000.html
- https://security.gentoo.org/glsa/202007-44
- https://www.debian.org/security/2018/dsa-4129
- https://bugzilla.redhat.com/show_bug.cgi?id=1547885
