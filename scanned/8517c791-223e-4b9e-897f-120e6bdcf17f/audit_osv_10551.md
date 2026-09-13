# [H] CVE-2017-16997

## Summary
Severity: High
Advisory: CVE-2017-16997
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-18
Source: https://osv.dev/vulnerability/CVE-2017-16997
Type: osv

## Details
elf/dl-load.c in the GNU C Library (aka glibc or libc6) 2.19 through 2.26 mishandles RPATH and RUNPATH containing $ORIGIN for a privileged (setuid or AT_SECURE) program, which allows local users to gain privileges via a Trojan horse library in the current working directory, related to the fillin_rpath and decompose_rpath functions. This is associated with misinterpretion of an empty RPATH/RUNPATH token as the "./" directory. NOTE: this configuration of RPATH/RUNPATH for a privileged program is apparently very uncommon; most likely, no such program is shipped with any common Linux distribution.

## References
- http://www.securityfocus.com/bid/102228
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3092
- https://bugs.debian.org/884615
- https://sourceware.org/bugzilla/show_bug.cgi?id=22625
- https://sourceware.org/ml/libc-alpha/2017-12/msg00528.html
