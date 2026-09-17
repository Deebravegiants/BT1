# [H] CVE-2024-46952

## Summary
Severity: High
Advisory: CVE-2024-46952
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-10
Source: https://osv.dev/vulnerability/CVE-2024-46952
Type: osv

## Details
An issue was discovered in pdf/pdf_xref.c in Artifex Ghostscript before 10.04.0. There is a buffer overflow during handling of a PDF XRef stream (related to W array values).

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=708001
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/commit/?id=b1f0827c30f59a2dcbc8a39e42cace7a1de35f7f
- https://github.com/ArtifexSoftware/ghostpdl/blob/master/doc/News.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46952.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46952
