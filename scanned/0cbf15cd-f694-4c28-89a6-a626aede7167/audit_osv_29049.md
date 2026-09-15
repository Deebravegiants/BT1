# [C] Revert "xsk: Support redirect to any socket bound to the same umem"

## Summary
Severity: Critical
Advisory: CVE-2024-39293
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-39293
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "xsk: Support redirect to any socket bound to the same umem"

This reverts commit 2863d665ea41282379f108e4da6c8a2366ba66db.

This patch introduced a potential kernel crash when multiple napi instances
redirect to the same AF_XDP socket. By removing the queue_index check, it is
possible for multiple napi instances to access the Rx ring at the same time,
which will result in a corrupted ring state which can lead to a crash when
flushing the rings in __xsk_flush(). This can happen when the linked list of
sockets to flush gets corrupted by concurrent accesses. A quick and small fix
is not possible, so let us revert this for now.

## References
- https://git.kernel.org/stable/c/19cb40b1064566ea09538289bfcf5bc7ecb9b6f5
- https://git.kernel.org/stable/c/7fcf26b315bbb728036da0862de6b335da83dff2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39293.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39293
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
