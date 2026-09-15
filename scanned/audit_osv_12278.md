# [M] CVE-2018-1121

## Summary
Severity: Medium
Advisory: CVE-2018-1121
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/CVE-2018-1121
Type: osv

## Details
procps-ng, procps is vulnerable to a process hiding through race condition. Since the kernel's proc_pid_readdir() returns PID entries in ascending numeric order, a process occupying a high PID can use inotify events to determine when the process list is being scanned, and fork/exec to obtain a lower PID, thus avoiding enumeration. An unprivileged attacker can hide a process from procps-ng's utilities by exploiting a race condition in reading /proc/PID entries. This vulnerability affects procps and procps-ng up to version 3.3.15, newer versions might be affected also.

## References
- http://www.securityfocus.com/bid/104214
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1121
- http://seclists.org/oss-sec/2018/q2/122
- https://www.exploit-db.com/exploits/44806/
- https://www.qualys.com/2018/05/17/procps-ng-audit-report-advisory.txt
