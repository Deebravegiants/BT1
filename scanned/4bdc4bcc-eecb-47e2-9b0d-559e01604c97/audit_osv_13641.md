# [M] CVE-2018-20671

## Summary
Severity: Medium
Advisory: CVE-2018-20671
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-04
Source: https://osv.dev/vulnerability/CVE-2018-20671
Type: osv

## Details
load_specific_debug_section in objdump.c in GNU Binutils through 2.31.1 contains an integer overflow vulnerability that can trigger a heap-based buffer overflow via a crafted section size.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=11fa9f134fd658075c6f74499c780df045d9e9ca
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/106457
- https://sourceware.org/bugzilla/show_bug.cgi?id=24005
