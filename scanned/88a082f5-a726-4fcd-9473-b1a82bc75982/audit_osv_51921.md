# [M] CVE-2021-45480

## Summary
Severity: Medium
Advisory: CVE-2021-45480
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-12-24
Source: https://osv.dev/vulnerability/CVE-2021-45480
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.15.11. There is a memory leak in the __rds_conn_create() function in net/rds/connection.c in a certain combination of circumstances.

## References
- https://www.debian.org/security/2022/dsa-5050
- https://www.debian.org/security/2022/dsa-5096
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.11
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://github.com/torvalds/linux/commit/5f9562ebe710c307adc5f666bf1a2162ee7977c0
