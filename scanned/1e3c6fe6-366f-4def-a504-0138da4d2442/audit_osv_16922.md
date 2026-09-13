# [M] CVE-2020-10723

## Summary
Severity: Medium
Advisory: CVE-2020-10723
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/CVE-2020-10723
Type: osv

## Details
A memory corruption issue was found in DPDK versions 17.05 and above. This flaw is caused by an integer truncation on the index of a payload. Under certain circumstances, the index (a UInt) is copied and truncated into a uint16, which can lead to out of bound indexing and possible memory corruption.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HRHKFVV4MRWNNJOYQOVP64L4UVWYPEO4/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00045.html
- https://usn.ubuntu.com/4362-1/
- https://www.openwall.com/lists/oss-security/2020/05/18/2
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10723
- https://bugs.dpdk.org/show_bug.cgi?id=268
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
