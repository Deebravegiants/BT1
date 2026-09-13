# [H] CVE-2019-19071

## Summary
Severity: High
Advisory: CVE-2019-19071
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19071
Type: osv

## Details
A memory leak in the rsi_send_beacon() function in drivers/net/wireless/rsi/rsi_91x_mgmt.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering rsi_prepare_beacon() failures, aka CID-d563131ef23c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3PSDE6PTOTVBK2YTKB2TFQP2SUBVSNF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PY7LJMSPAGRIKABJPDKQDTXYW3L5RX2T/
- https://usn.ubuntu.com/4287-1/
- https://usn.ubuntu.com/4287-2/
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4258-1/
- https://usn.ubuntu.com/4284-1/
- https://github.com/torvalds/linux/commit/d563131ef23cbc756026f839a82598c8445bc45f
