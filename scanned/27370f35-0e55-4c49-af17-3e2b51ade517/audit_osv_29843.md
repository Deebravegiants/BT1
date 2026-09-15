# [M] CVE-2024-46955

## Summary
Severity: Medium
Advisory: CVE-2024-46955
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-11-10
Source: https://osv.dev/vulnerability/CVE-2024-46955
Type: osv

## Details
An issue was discovered in psi/zcolor.c in Artifex Ghostscript before 10.04.0. There is an out-of-bounds read when reading color in Indexed color space.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=707990
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/commit/?id=85bd9d2f4b792fe67aef22f1a4117457461b8ba6
- https://github.com/ArtifexSoftware/ghostpdl/blob/master/doc/News.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00023.html
- https://www.suse.com/support/update/announcement/2024/suse-su-20243942-1/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46955.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46955
