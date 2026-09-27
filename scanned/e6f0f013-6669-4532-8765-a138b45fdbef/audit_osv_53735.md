# [M] CVE-2023-2162

## Summary
Severity: Medium
Advisory: CVE-2023-2162
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-19
Source: https://osv.dev/vulnerability/CVE-2023-2162
Type: osv

## Details
A use-after-free vulnerability was found in iscsi_sw_tcp_session_create in drivers/scsi/iscsi_tcp.c in SCSI sub-component in the Linux Kernel. In this flaw an attacker could leak kernel internal information.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://www.spinics.net/lists/linux-scsi/msg181542.html
