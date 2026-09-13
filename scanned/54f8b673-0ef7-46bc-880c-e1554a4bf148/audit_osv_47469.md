# [M] CVE-2016-6136

## Summary
Severity: Medium
Advisory: CVE-2016-6136
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6136
Type: osv

## Details
Race condition in the audit_log_single_execve_arg function in kernel/auditsc.c in the Linux kernel through 4.7 allows local users to bypass intended character-set restrictions or disrupt system-call auditing by changing a certain string, aka a "double fetch" vulnerability.

## References
- https://source.android.com/security/bulletin/2016-11-01.html
- http://www.securityfocus.com/bid/91558
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- http://rhn.redhat.com/errata/RHSA-2017-0307.html
- http://www.securityfocus.com/archive/1/538835/30/0/threaded
- https://bugzilla.redhat.com/show_bug.cgi?id=1353533
- https://bugzilla.kernel.org/show_bug.cgi?id=120681
- https://github.com/linux-audit/audit-kernel/issues/18
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=43761473c254b45883a64441dd0bc85a42f3645c
- https://github.com/torvalds/linux/commit/43761473c254b45883a64441dd0bc85a42f3645c
