# [M] CVE-2018-12434

## Summary
Severity: Medium
Advisory: CVE-2018-12434
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-15
Source: https://osv.dev/vulnerability/CVE-2018-12434
Type: osv

## Details
LibreSSL before 2.6.5 and 2.7.x before 2.7.4 allows a memory-cache side-channel attack on DSA and ECDSA signatures, aka the Return Of the Hidden Number Problem or ROHNP. To discover a key, the attacker needs access to either the local machine or a different virtual machine on the same physical host.

## References
- https://ftp.openbsd.org/pub/OpenBSD/LibreSSL/libressl-2.6.5-relnotes.txt
- https://ftp.openbsd.org/pub/OpenBSD/LibreSSL/libressl-2.7.4-relnotes.txt
- https://www.nccgroup.trust/us/our-research/technical-advisory-return-of-the-hidden-number-problem/
