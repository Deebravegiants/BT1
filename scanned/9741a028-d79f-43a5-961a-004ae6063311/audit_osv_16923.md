# [M] CVE-2020-10724

## Summary
Severity: Medium
Advisory: CVE-2020-10724
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/CVE-2020-10724
Type: osv

## Details
A vulnerability was found in DPDK versions 18.11 and above. The vhost-crypto library code is missing validations for user-supplied values, potentially allowing an information leak through an out-of-bounds memory read.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HRHKFVV4MRWNNJOYQOVP64L4UVWYPEO4/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00045.html
- https://usn.ubuntu.com/4362-1/
- https://www.openwall.com/lists/oss-security/2020/05/18/2
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10724
- https://bugs.dpdk.org/show_bug.cgi?id=269
