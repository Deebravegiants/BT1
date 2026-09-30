# [M] CVE-2020-10726

## Summary
Severity: Medium
Advisory: CVE-2020-10726
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-20
Source: https://osv.dev/vulnerability/CVE-2020-10726
Type: osv

## Details
A vulnerability was found in DPDK versions 19.11 and above. A malicious container that has direct access to the vhost-user socket can keep sending VHOST_USER_GET_INFLIGHT_FD messages, causing a resource leak (file descriptors and virtual memory), which may result in a denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HRHKFVV4MRWNNJOYQOVP64L4UVWYPEO4/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00045.html
- https://www.openwall.com/lists/oss-security/2020/05/18/2
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10726
- https://bugs.dpdk.org/show_bug.cgi?id=271
- https://www.oracle.com/security-alerts/cpujan2021.html
