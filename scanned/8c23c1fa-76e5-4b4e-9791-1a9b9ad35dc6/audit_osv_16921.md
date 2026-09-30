# [M] CVE-2020-10722

## Summary
Severity: Medium
Advisory: CVE-2020-10722
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/CVE-2020-10722
Type: osv

## Details
A vulnerability was found in DPDK versions 18.05 and above. A missing check for an integer overflow in vhost_user_set_log_base() could result in a smaller memory map than requested, possibly allowing memory corruption.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HRHKFVV4MRWNNJOYQOVP64L4UVWYPEO4/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00045.html
- https://usn.ubuntu.com/4362-1/
- https://www.openwall.com/lists/oss-security/2020/05/18/2
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10722
- https://bugs.dpdk.org/show_bug.cgi?id=267
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
