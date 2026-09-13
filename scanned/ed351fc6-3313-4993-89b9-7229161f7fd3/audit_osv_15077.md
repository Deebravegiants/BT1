# [H] CVE-2019-13272

## Summary
Severity: High
Advisory: CVE-2019-13272
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-13272
Type: osv

## Details
In the Linux kernel before 5.1.17, ptrace_link in kernel/ptrace.c mishandles the recording of the credentials of a process that wants to create a ptrace relationship, which allows local users to obtain root access by leveraging certain scenarios with a parent-child process relationship, where a parent drops privileges and calls execve (potentially allowing control by an attacker). One contributing factor is an object lifetime issue (which can also cause a panic). Another contributing factor is incorrect marking of a ptrace relationship as privileged, which is exploitable through (for example) Polkit's pkexec helper with PTRACE_TRACEME. NOTE: SELinux deny_ptrace might be a usable workaround in some environments.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-13272
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OGRK5LYWBJ4E4SRI4DKX367NHYSI3VOH/
- https://security.netapp.com/advisory/ntap-20190806-0001/
- https://www.debian.org/security/2019/dsa-4484
- http://packetstormsecurity.com/files/153663/Linux-PTRACE_TRACEME-Broken-Permission-Object-Lifetime-Handling.html
- http://packetstormsecurity.com/files/153702/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://support.f5.com/csp/article/K91025336?utm_source=f5support&amp%3Butm_medium=RSS
- https://access.redhat.com/errata/RHSA-2019:2809
- https://usn.ubuntu.com/4095-1/
- https://usn.ubuntu.com/4117-1/
- https://usn.ubuntu.com/4094-1/
- https://access.redhat.com/errata/RHSA-2019:2411
- https://lists.debian.org/debian-lts-announce/2019/07/msg00022.html
- https://lists.debian.org/debian-lts-announce/2019/07/msg00023.html
- https://support.f5.com/csp/article/K91025336
- https://usn.ubuntu.com/4093-1/
- https://access.redhat.com/errata/RHSA-2019:2405
- https://usn.ubuntu.com/4118-1/
- https://seclists.org/bugtraq/2019/Jul/30
- https://seclists.org/bugtraq/2019/Jul/33
