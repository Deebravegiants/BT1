# [H] CVE-2023-0179

## Summary
Severity: High
Advisory: CVE-2023-0179
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-0179
Type: osv

## Details
A buffer overflow vulnerability was found in the Netfilter subsystem in the Linux Kernel. This issue could allow the leakage of both stack and heap addresses, and potentially allow Local Privilege Escalation to the root user via arbitrary code execution.

## References
- http://packetstormsecurity.com/files/171601/Kernel-Live-Patch-Security-Notice-LNS-0093-1.html
- https://security.netapp.com/advisory/ntap-20230511-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=2161713
- https://seclists.org/oss-sec/2023/q1/20
