# [H] CVE-2024-46956

## Summary
Severity: High
Advisory: CVE-2024-46956
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-11-10
Source: https://osv.dev/vulnerability/CVE-2024-46956
Type: osv

## Details
An issue was discovered in psi/zfile.c in Artifex Ghostscript before 10.04.0. Out-of-bounds data access in filenameforall can lead to arbitrary code execution.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=707895
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/commit/?id=f4151f12db32cd3ed26c24327de714bf2c3ed6ca
- https://github.com/ArtifexSoftware/ghostpdl/blob/master/doc/News.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00023.html
- https://www.suse.com/support/update/announcement/2024/suse-su-20243942-1/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46956.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46956
