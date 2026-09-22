# [H] net/rds: handle zerocopy send cleanup before the message is queued

## Summary
Severity: High
Advisory: CVE-2026-43502
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-43502
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/rds: handle zerocopy send cleanup before the message is queued

A zerocopy send can fail after user pages have been pinned but before
the message is attached to the sending socket.

The purge path currently infers zerocopy state from rm->m_rs, so an
unqueued message can be cleaned up as if it owned normal payload pages.
However, zerocopy ownership is really determined by the presence of
op_mmp_znotifier, regardless of whether the message has reached the
socket queue.

Capture op_mmp_znotifier up front in rds_message_purge() and use it as
the cleanup discriminator. If the message is already associated with a
socket, keep the existing completion path. Otherwise, drop the pinned
page accounting directly and release the notifier before putting the
payload pages.

This keeps early send failure cleanup consistent with the zerocopy
lifetime rules without changing the normal queued completion path.

## References
- https://git.kernel.org/stable/c/0f5c185fc79a59ee9991234dd6d2a3e5afa6e75b
- https://git.kernel.org/stable/c/14ef6fd18db2494098b21e0471bf27a1d8e9993e
- https://git.kernel.org/stable/c/1e262db7675e27f42c3f3f47d6011855f4454f24
- https://git.kernel.org/stable/c/21d70744e6d3bbf9293aa1ee6fba7c53ad75275e
- https://git.kernel.org/stable/c/3abc8983b2bae3f487f77d9da5527d7d6b210d46
- https://git.kernel.org/stable/c/44b550d88b267320459d518c0743a241ab2108fa
- https://git.kernel.org/stable/c/46662f7dc59475995609bf3e9d27eb36f4acf26f
- https://git.kernel.org/stable/c/e9aefdc5c53fe9aed108c14e3d155710a1bb14c9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43502.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43502
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
