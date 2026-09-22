# [M] CVE-2016-1000341

## Summary
Severity: Medium
Advisory: CVE-2016-1000341
Aliases: GHSA-r9ch-m4fh-fc7q
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-04
Source: https://osv.dev/vulnerability/CVE-2016-1000341
Type: osv

## Details
In the Bouncy Castle JCE Provider version 1.55 and earlier DSA signature generation is vulnerable to timing attack. Where timings can be closely observed for the generation of signatures, the lack of blinding in 1.55, or earlier, may allow an attacker to gain information about the signature's k value and ultimately the private value as well.

## References
- https://usn.ubuntu.com/3727-1/
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://access.redhat.com/errata/RHSA-2018:2669
- https://access.redhat.com/errata/RHSA-2018:2927
- https://lists.debian.org/debian-lts-announce/2018/07/msg00009.html
- https://security.netapp.com/advisory/ntap-20181127-0004/
- https://github.com/bcgit/bc-java/commit/acaac81f96fec91ab45bd0412beaf9c3acd8defa#diff-e75226a9ca49217a7276b29242ec59ce
