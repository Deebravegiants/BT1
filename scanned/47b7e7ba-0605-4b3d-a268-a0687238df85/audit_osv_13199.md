# [M] CVE-2018-18586

## Summary
Severity: Medium
Advisory: CVE-2018-18586
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-10-23
Source: https://osv.dev/vulnerability/CVE-2018-18586
Type: osv

## Details
chmextract.c in the chmextract sample program, as distributed with libmspack before 0.8alpha, does not protect against absolute/relative pathnames in CHM files, leading to Directory Traversal. NOTE: the vendor disputes that this is a libmspack vulnerability, because chmextract.c was only intended as a source-code example, not a supported application

## References
- https://bugs.debian.org/911639
- https://security.gentoo.org/glsa/201903-20
- https://www.openwall.com/lists/oss-security/2018/10/22/1
- https://github.com/kyz/libmspack/commit/7cadd489698be117c47efcadd742651594429e6d
