# [M] CVE-2019-1010190

## Summary
Severity: Medium
Advisory: CVE-2019-1010190
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-24
Source: https://osv.dev/vulnerability/CVE-2019-1010190
Type: osv

## Details
mgetty prior to 1.2.1 is affected by: out-of-bounds read. The impact is: DoS, the program may crash if the memory is not mapped. The component is: putwhitespan() in g3/pbm2g3.c. The attack vector is: Local, the victim must open a specially crafted file. The fixed version is: 1.2.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00016.html
- https://www.x41-dsec.de/lab/advisories/x41-2018-007-mgetty/
