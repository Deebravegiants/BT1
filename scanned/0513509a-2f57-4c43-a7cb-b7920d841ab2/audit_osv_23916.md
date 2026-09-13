# [H] mptcp: fix race on unaccepted mptcp sockets

## Summary
Severity: High
Advisory: CVE-2022-49669
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49669
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: fix race on unaccepted mptcp sockets

When the listener socket owning the relevant request is closed,
it frees the unaccepted subflows and that causes later deletion
of the paired MPTCP sockets.

The mptcp socket's worker can run in the time interval between such delete
operations. When that happens, any access to msk->first will cause an UaF
access, as the subflow cleanup did not cleared such field in the mptcp
socket.

Address the issue explicitly traversing the listener socket accept
queue at close time and performing the needed cleanup on the pending
msk.

Note that the locking is a bit tricky, as we need to acquire the msk
socket lock, while still owning the subflow socket one.

## References
- https://git.kernel.org/stable/c/6aeed9045071f2252ff4e98fc13d1e304f33e5b0
- https://git.kernel.org/stable/c/a8a3e95c74e48c2c9b07b81fafda9122993f2e12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49669.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49669
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
