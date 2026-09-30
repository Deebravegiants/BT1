# [M] CVE-2019-18603

## Summary
Severity: Medium
Advisory: CVE-2019-18603
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-10-29
Source: https://osv.dev/vulnerability/CVE-2019-18603
Type: osv

## Details
OpenAFS before 1.6.24 and 1.8.x before 1.8.5 is prone to information leakage upon certain error conditions because uninitialized RPC output variables are sent over the network to a peer.

## References
- https://lists.debian.org/debian-lts-announce/2019/11/msg00002.html
- https://openafs.org/pages/security/OPENAFS-SA-2019-001.txt
