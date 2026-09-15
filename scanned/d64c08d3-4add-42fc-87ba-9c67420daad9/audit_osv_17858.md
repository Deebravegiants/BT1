# [M] CVE-2020-21047

## Summary
Severity: Medium
Advisory: CVE-2020-21047
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-21047
Type: osv

## Details
The libcpu component which is used by libasm of elfutils version 0.177 (git 47780c9e), suffers from denial-of-service vulnerability caused by application crashes due to out-of-bounds write (CWE-787), off-by-one error (CWE-193) and reachable assertion (CWE-617); to exploit the vulnerability, the attackers need to craft certain ELF files which bypass the missing bound checks.

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00026.html
- https://sourceware.org/git/?p=elfutils.git%3Ba=commitdiff%3Bh=99dc63b10b3878616b85df2dfd2e4e7103e414b8
- https://sourceware.org/bugzilla/show_bug.cgi?id=25068
