# [H] CVE-2023-5178

## Summary
Severity: High
Advisory: CVE-2023-5178
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-01
Source: https://osv.dev/vulnerability/CVE-2023-5178
Type: osv

## Details
A use-after-free vulnerability was found in drivers/nvme/target/tcp.c` in `nvmet_tcp_free_crypto` due to a logical bug in the NVMe/TCP subsystem in the Linux kernel. This issue may allow a malicious user to cause a use-after-free and double-free problem, which may permit remote code execution or lead to local privilege escalation.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00005.html
- https://access.redhat.com/errata/RHSA-2023:7370
- https://access.redhat.com/errata/RHSA-2023:7379
- https://access.redhat.com/errata/RHSA-2023:7418
- https://access.redhat.com/errata/RHSA-2023:7559
- https://access.redhat.com/errata/RHSA-2024:0554
- https://access.redhat.com/errata/RHSA-2024:1268
- https://access.redhat.com/errata/RHSA-2024:0386
- https://access.redhat.com/errata/RHSA-2024:0432
- https://access.redhat.com/errata/RHSA-2024:1269
- https://access.redhat.com/errata/RHSA-2024:1278
- https://access.redhat.com/security/cve/CVE-2023-5178
- https://security.netapp.com/advisory/ntap-20231208-0004/
- https://access.redhat.com/errata/RHSA-2024:0412
- https://access.redhat.com/errata/RHSA-2023:7548
- https://access.redhat.com/errata/RHSA-2023:7549
- https://access.redhat.com/errata/RHSA-2023:7554
- https://access.redhat.com/errata/RHSA-2024:0340
- https://access.redhat.com/errata/RHSA-2024:0575
- https://access.redhat.com/errata/RHSA-2023:7551
