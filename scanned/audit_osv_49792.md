# [M] CVE-2019-19072

## Summary
Severity: Medium
Advisory: CVE-2019-19072
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19072
Type: osv

## Details
A memory leak in the predicate_parse() function in kernel/trace/trace_events_filter.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption), aka CID-96c5c6e6a5b6.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3PSDE6PTOTVBK2YTKB2TFQP2SUBVSNF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PY7LJMSPAGRIKABJPDKQDTXYW3L5RX2T/
- https://usn.ubuntu.com/4225-1/
- https://usn.ubuntu.com/4225-2/
- https://usn.ubuntu.com/4226-1/
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://github.com/torvalds/linux/commit/96c5c6e6a5b6db592acae039fed54b5c8844cd35
