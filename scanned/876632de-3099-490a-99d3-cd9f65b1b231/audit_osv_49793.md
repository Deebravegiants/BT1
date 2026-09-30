# [M] CVE-2019-19073

## Summary
Severity: Medium
Advisory: CVE-2019-19073
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19073
Type: osv

## Details
Memory leaks in drivers/net/wireless/ath/ath9k/htc_hst.c in the Linux kernel through 5.3.11 allow attackers to cause a denial of service (memory consumption) by triggering wait_for_completion_timeout() failures. This affects the htc_config_pipe_credits() function, the htc_setup_complete() function, and the htc_connect_service() function, aka CID-853acf7caf10.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PY7LJMSPAGRIKABJPDKQDTXYW3L5RX2T/
- https://usn.ubuntu.com/4526-1/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3PSDE6PTOTVBK2YTKB2TFQP2SUBVSNF/
- https://usn.ubuntu.com/4527-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://github.com/torvalds/linux/commit/853acf7caf10b828102d92d05b5c101666a6142b
