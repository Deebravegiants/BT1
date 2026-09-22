# [H] CVE-2023-3269

## Summary
Severity: High
Advisory: CVE-2023-3269
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-11
Source: https://osv.dev/vulnerability/CVE-2023-3269
Type: osv

## Details
A vulnerability exists in the memory management subsystem of the Linux kernel. The lock handling for accessing and updating virtual memory areas (VMAs) is incorrect, leading to use-after-free problems. This issue can be successfully exploited to execute arbitrary kernel code, escalate containers, and gain root privileges.

## References
- http://seclists.org/fulldisclosure/2023/Jul/43
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U6AAA64CUPSMBW6XDTXPQJ3KQWYQ4K7L/
- https://access.redhat.com/security/cve/CVE-2023-3269
- https://security.netapp.com/advisory/ntap-20230908-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=2215268
- http://www.openwall.com/lists/oss-security/2023/07/28/1
- http://www.openwall.com/lists/oss-security/2023/08/25/1
- http://www.openwall.com/lists/oss-security/2023/08/25/4
- https://www.openwall.com/lists/oss-security/2023/07/05/1
