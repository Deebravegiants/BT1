# [H] io_uring/poll: fix signed comparison in io_poll_get_ownership()

## Summary
Severity: High
Advisory: CVE-2026-52933
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52933
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/poll: fix signed comparison in io_poll_get_ownership()

io_poll_get_ownership() uses a signed comparison to check whether
poll_refs has reached the threshold for the slowpath:

    if (unlikely(atomic_read(&req->poll_refs) >= IO_POLL_REF_BIAS))

atomic_read() returns int (signed). When IO_POLL_CANCEL_FLAG
(BIT(31)) is set in poll_refs, the value becomes negative in
signed arithmetic, so the >= 128 comparison always evaluates to
false and the slowpath is never taken.

Fix this by casting the atomic_read() result to unsigned int
before the comparison, so that the cancel flag is treated as a
large positive value and correctly triggers the slowpath.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/326941b22806cbf2df1fbfe902b7908b368cce42
- https://git.kernel.org/stable/c/81bf96b0abbfa4cd47ea32e12596aed3855fb2f3
- https://git.kernel.org/stable/c/c6d191164dc81838d8dbf452a6000f68c558d1ae
- https://git.kernel.org/stable/c/cf522703d4f194991615763697ae25a3f9539763
- https://git.kernel.org/stable/c/ea0697129807d718037f618221037aa0660ee3c5
- https://git.kernel.org/stable/c/fc47043f3d9af3efa407665b47f8378ec691ba18
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52933.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52933
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
