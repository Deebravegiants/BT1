# [C] CVE-2018-11236

## Summary
Severity: Critical
Advisory: CVE-2018-11236
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-18
Source: https://osv.dev/vulnerability/CVE-2018-11236
Type: osv

## Details
stdlib/canonicalize.c in the GNU C Library (aka glibc or libc6) 2.27 and earlier, when processing very long pathname arguments to the realpath function, could encounter an integer overflow on 32-bit architectures, leading to a stack-based buffer overflow and, potentially, arbitrary code execution.

## References
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=5460617d1567657621107d895ee2dd83bc1f88f2
- https://usn.ubuntu.com/4416-1/
- http://www.securityfocus.com/bid/104255
- https://access.redhat.com/errata/RHBA-2019:0327
- https://security.netapp.com/advisory/ntap-20190329-0001/
- https://security.netapp.com/advisory/ntap-20190401-0001/
- https://sourceware.org/bugzilla/show_bug.cgi?id=22786
- https://access.redhat.com/errata/RHSA-2018:3092
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
