# [M] CVE-2019-19062

## Summary
Severity: Medium
Advisory: CVE-2019-19062
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19062
Type: osv

## Details
A memory leak in the crypto_report() function in crypto/crypto_user_base.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering crypto_report_alg() failures, aka CID-ffdde5932042.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PY7LJMSPAGRIKABJPDKQDTXYW3L5RX2T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3PSDE6PTOTVBK2YTKB2TFQP2SUBVSNF/
- https://seclists.org/bugtraq/2020/Jan/10
- https://usn.ubuntu.com/4254-1/
- https://usn.ubuntu.com/4254-2/
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4258-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://usn.ubuntu.com/4287-2/
- https://usn.ubuntu.com/4284-1/
- https://usn.ubuntu.com/4287-1/
- http://packetstormsecurity.com/files/155890/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://github.com/torvalds/linux/commit/ffdde5932042600c6807d46c1550b28b0db6a3bc
