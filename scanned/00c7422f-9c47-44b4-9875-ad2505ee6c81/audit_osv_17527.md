# [C] CVE-2020-15900

## Summary
Severity: Critical
Advisory: CVE-2020-15900
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-28
Source: https://osv.dev/vulnerability/CVE-2020-15900
Type: osv

## Details
A memory corruption issue was found in Artifex Ghostscript 9.50 and 9.52. Use of a non-standard PostScript operator can allow overriding of file access controls. The 'rsearch' calculation for the 'post' size resulted in a size that was too large, and could underflow to max uint32_t. This was fixed in commit 5d499272b95a6b890a1397e11d20937de000d31b.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=log
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=5d499272b95a6b890a1397e11d20937de000d31b
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00006.html
- https://artifex.com/security-advisories/CVE-2020-15900
- https://security.gentoo.org/glsa/202008-20
- https://usn.ubuntu.com/4445-1/
- https://github.com/ArtifexSoftware/ghostpdl/commit/5d499272b95a6b890a1397e11d20937de000d31b
- https://github.com/ArtifexSoftware/ghostpdl/commits/master/psi/zstring.c
