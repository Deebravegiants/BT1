# [M] CVE-2019-19769

## Summary
Severity: Medium
Advisory: CVE-2019-19769
Aliases: A-150693748, ASB-A-150693748
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-12
Source: https://osv.dev/vulnerability/CVE-2019-19769
Type: osv

## Details
In the Linux kernel 5.3.10, there is a use-after-free (read) in the perf_trace_lock_acquire function (related to include/trace/events/lock.h).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TF4PQZBEPNXDSK5DOBMW54OCLP25FTCD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VJSIZWKW7RDHKU3CHC5BFAQI43NVHLUQ/
- https://usn.ubuntu.com/4368-1/
- https://usn.ubuntu.com/4369-1/
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://bugzilla.kernel.org/show_bug.cgi?id=205705
