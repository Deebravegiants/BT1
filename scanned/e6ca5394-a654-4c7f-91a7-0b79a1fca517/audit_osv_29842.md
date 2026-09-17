# [H] CVE-2024-46954

## Summary
Severity: High
Advisory: CVE-2024-46954
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-10
Source: https://osv.dev/vulnerability/CVE-2024-46954
Type: osv

## Details
An issue was discovered in decode_utf8 in base/gp_utf8.c in Artifex Ghostscript before 10.04.0. Overlong UTF-8 encoding leads to possible ../ directory traversal.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=707788
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/commit/?id=55f587dd039282316f512e1bea64218fd991f934
- https://github.com/ArtifexSoftware/ghostpdl/blob/master/doc/News.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46954.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46954
