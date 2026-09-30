# [M] CVE-2019-19066

## Summary
Severity: Medium
Advisory: CVE-2019-19066
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19066
Type: osv

## Details
A memory leak in the bfad_im_get_stats() function in drivers/scsi/bfa/bfad_attr.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering bfa_port_get_stats() failures, aka CID-0e62395da2bd.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3PSDE6PTOTVBK2YTKB2TFQP2SUBVSNF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PY7LJMSPAGRIKABJPDKQDTXYW3L5RX2T/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4286-1/
- https://usn.ubuntu.com/4300-1/
- https://usn.ubuntu.com/4301-1/
- https://usn.ubuntu.com/4302-1/
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://usn.ubuntu.com/4286-2/
- https://github.com/torvalds/linux/commit/0e62395da2bd5166d7c9e14cbc7503b256a34cb0
