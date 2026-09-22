# [H] CVE-2021-4197

## Summary
Severity: High
Advisory: CVE-2021-4197
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-23
Source: https://osv.dev/vulnerability/CVE-2021-4197
Type: osv

## Details
An unprivileged write to the file handler flaw in the Linux kernel's control groups and namespaces subsystem was found in the way users have access to some less privileged process that are controlled by cgroups and have higher privileged parent process. It is actually both for cgroup2 and cgroup1 versions of control groups. A local user could use this flaw to crash the system or escalate their privileges on the system.

## References
- https://lore.kernel.org/lkml/20211209214707.805617-1-tj%40kernel.org/T/
- https://security.netapp.com/advisory/ntap-20220602-0006/
- https://www.debian.org/security/2022/dsa-5127
- https://www.debian.org/security/2022/dsa-5173
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2035652
