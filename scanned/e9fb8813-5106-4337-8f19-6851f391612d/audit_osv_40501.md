# [H] media: rzv2h-ivc: Fix concurrent buffer list access

## Summary
Severity: High
Advisory: CVE-2026-53380
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53380
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: rzv2h-ivc: Fix concurrent buffer list access

The list of buffers (`rzv2h_ivc::buffers.queue`) is protected by a
spinlock (`rzv2h_ivc::buffers.lock`). However, in
`rzv2h_ivc_transfer_buffer()`, which runs in a separate workqueue, the
`list_del()` call is executed without holding the spinlock, which makes
it possible for the list to be concurrently modified

Fix that by removing a buffer from the list in the lock protected section.

[assign ivc->buffers.curr in critical section as reported by Barnabas]

## References
- https://git.kernel.org/stable/c/72773ff1cdfaebc593f53b1719b2c1773ecf8c43
- https://git.kernel.org/stable/c/c746522bd3264132ab2e2382e96e19cdb8a6c1ba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53380.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53380
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
