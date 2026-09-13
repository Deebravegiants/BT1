# [H] CVE-2020-27792

## Summary
Severity: High
Advisory: CVE-2020-27792
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2022-08-19
Source: https://osv.dev/vulnerability/CVE-2020-27792
Type: osv

## Details
A heap-based buffer overwrite vulnerability was found in GhostScript's lp8000_print_page() function in the gdevlp8k.c file. This flaw allows an attacker to trick a user into opening a crafted PDF file, triggering the heap buffer overflow that could lead to memory corruption or a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2022/09/msg00005.html
- https://access.redhat.com/security/cve/CVE-2020-27792
- https://git.ghostscript.com/?p=ghostpdl.git;a=commitdiff;h=4f6bc662909ab79e8fbe9822afb36e8a0eafc2b7
- https://bugs.ghostscript.com/show_bug.cgi?id=701844
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=4f6bc662909ab79e8fbe9822afb36e8a0eafc2b7
- https://access.redhat.com/errata/RHSA-2025:4362
- https://bugzilla.redhat.com/show_bug.cgi?id=2247179
