# [H] CVE-2020-10725

## Summary
Severity: High
Advisory: CVE-2020-10725
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-05-20
Source: https://osv.dev/vulnerability/CVE-2020-10725
Type: osv

## Details
A flaw was found in DPDK version 19.11 and above that allows a malicious guest to cause a segmentation fault of the vhost-user backend application running on the host, which could result in a loss of connectivity for the other guests running on that host. This is caused by a missing validity check of the descriptor address in the function `virtio_dev_rx_batch_packed()`.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HRHKFVV4MRWNNJOYQOVP64L4UVWYPEO4/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00045.html
- https://www.openwall.com/lists/oss-security/2020/05/18/2
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10725
- https://bugs.dpdk.org/show_bug.cgi?id=270
- https://www.oracle.com/security-alerts/cpujan2021.html
