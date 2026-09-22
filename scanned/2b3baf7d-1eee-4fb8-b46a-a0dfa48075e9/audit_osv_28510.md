# [H] CVE-2024-33871

## Summary
Severity: High
Advisory: CVE-2024-33871
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-03
Source: https://osv.dev/vulnerability/CVE-2024-33871
Type: osv

## Details
An issue was discovered in Artifex Ghostscript before 10.03.1. contrib/opvp/gdevopvp.c allows arbitrary code execution via a custom Driver library, exploitable via a crafted PostScript document. This occurs because the Driver parameter for opvp (and oprp) devices can have an arbitrary name for a dynamic library; this library is then loaded.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=707754
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/commit/?id=7145885041bb52cc23964f0aa2aec1b1c82b5908
- https://www.openwall.com/lists/oss-security/2024/06/28/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33871.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33871
