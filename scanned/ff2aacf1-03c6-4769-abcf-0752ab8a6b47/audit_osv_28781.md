# [M] CVE-2024-3652

## Summary
Severity: Medium
Advisory: CVE-2024-3652
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-11
Source: https://osv.dev/vulnerability/CVE-2024-3652
Type: osv

## Details
The Libreswan Project was notified of an issue causing libreswan to restart when using IKEv1 without specifying an esp= line. When the peer requests AES-GMAC, libreswan's default proposal handler causes an assertion failure and crashes and restarts. IKEv2 connections are not affected.

## References
- https://libreswan.org/security/CVE-2024-3652
- http://www.openwall.com/lists/oss-security/2024/04/18/2
