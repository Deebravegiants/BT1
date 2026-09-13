# [M] CVE-2024-29507

## Summary
Severity: Medium
Advisory: CVE-2024-29507
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2024-07-03
Source: https://osv.dev/vulnerability/CVE-2024-29507
Type: osv

## Details
Artifex Ghostscript before 10.03.0 sometimes has a stack-based buffer overflow via the CIDFSubstPath and CIDFSubstFont parameters.

## References
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=7745dbe24514
- https://bugs.ghostscript.com/show_bug.cgi?id=707510
- https://www.openwall.com/lists/oss-security/2024/07/03/7
