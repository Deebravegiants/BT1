# [H] mptcp: allow subflow rcv wnd to shrink

## Summary
Severity: High
Advisory: CVE-2026-53183
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53183
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: allow subflow rcv wnd to shrink

In MPTCP connection, the `window` field in the TCP header refers to the
MPTCP-level rcv_nxt and it's right edge should not move backward. Such
constraint is enforced at DSS option generation time.

At the same time, the TCP stack ensures independently that the TCP-level
rcv wnd right's edge does not move backward. That in turn causes artificial
inflating of the MPTCP rcv window when the incoming data is acked at the
TCP level and is OoO in the MPTCP sequence space (or lands in the backlog).

As a consequence, the incoming traffic can exceed the receiver rcvbuf size
even when the sender is not misbehaving.

Prevent such scenario forcibly allowing the TCP subflow to shrink the
TCP-level rcv wnd regardless of the current netns setting.

## References
- https://git.kernel.org/stable/c/653245266913f03fcf21cbca68eed5c197a33e52
- https://git.kernel.org/stable/c/aa3861f40ac32706d9e97bfac76984613e278788
- https://git.kernel.org/stable/c/b1fd13074f22105deec45aa02283e322733e0c2d
- https://git.kernel.org/stable/c/bf364b0f10b27679140699821f88af7f01e2a6e3
- https://git.kernel.org/stable/c/c297a4e65c50a2b807d9309b22615080faffa8f3
- https://git.kernel.org/stable/c/da23be77e1292cd611e736c3aa17da633d7ddce7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53183.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53183
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
