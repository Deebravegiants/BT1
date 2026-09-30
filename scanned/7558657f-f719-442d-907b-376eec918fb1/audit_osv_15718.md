# [H] CVE-2019-19050

## Summary
Severity: High
Advisory: CVE-2019-19050
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19050
Type: osv

## Details
A memory leak in the crypto_reportstat() function in crypto/crypto_user_stat.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering crypto_reportstat_alg() failures, aka CID-c03b04dcdba1.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3PSDE6PTOTVBK2YTKB2TFQP2SUBVSNF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PY7LJMSPAGRIKABJPDKQDTXYW3L5RX2T/
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4258-1/
- https://usn.ubuntu.com/4284-1/
- http://packetstormsecurity.com/files/156455/Kernel-Live-Patch-Security-Notice-LSN-0063-1.html
- https://github.com/torvalds/linux/commit/c03b04dcdba1da39903e23cc4d072abf8f68f2dd
