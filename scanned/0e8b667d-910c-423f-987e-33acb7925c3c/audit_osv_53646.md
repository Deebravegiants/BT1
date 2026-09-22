# [M] CVE-2023-1206

## Summary
Severity: Medium
Advisory: CVE-2023-1206
CVSS: 5.7 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-30
Source: https://osv.dev/vulnerability/CVE-2023-1206
Type: osv

## Details
A hash collision flaw was found in the IPv6 connection lookup table in the Linux kernel’s IPv6 functionality when a user makes a new kind of SYN flood attack. A user located in the local network or with a high bandwidth connection can increase the CPU usage of the server that accepts IPV6 connections up to 95%.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://security.netapp.com/advisory/ntap-20230929-0006/
- https://www.debian.org/security/2023/dsa-5480
- https://www.debian.org/security/2023/dsa-5492
- https://bugzilla.redhat.com/show_bug.cgi?id=2175903
