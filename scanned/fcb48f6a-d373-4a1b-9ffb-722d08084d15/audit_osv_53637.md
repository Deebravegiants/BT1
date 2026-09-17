# [M] CVE-2023-1074

## Summary
Severity: Medium
Advisory: CVE-2023-1074
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-1074
Type: osv

## Details
A memory leak flaw was found in the Linux kernel's Stream Control Transmission Protocol. This issue may occur when a user starts a malicious networking service and someone connects to this service. This could allow a local user to starve resources, causing a denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2173430
- https://www.openwall.com/lists/oss-security/2023/01/23/1
- https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git/commit/?id=458e279f861d3f61796894cd158b780765a1569f
- https://www.openwall.com/lists/oss-security/2023/01/23/1
- https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git/commit/?id=458e279f861d3f61796894cd158b780765a1569f
- https://bugzilla.redhat.com/show_bug.cgi?id=2173430
- http://www.openwall.com/lists/oss-security/2023/11/05/4
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
