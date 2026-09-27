# [H] smb: server: make use of smbdirect_socket.recv_io.credits.available

## Summary
Severity: High
Advisory: CVE-2026-31538
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31538
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.11, >=6.19.0 <6.19.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: server: make use of smbdirect_socket.recv_io.credits.available

The logic off managing recv credits by counting posted recv_io and
granted credits is racy.

That's because the peer might already consumed a credit,
but between receiving the incoming recv at the hardware
and processing the completion in the 'recv_done' functions
we likely have a window where we grant credits, which
don't really exist.

So we better have a decicated counter for the
available credits, which will be incremented
when we posted new recv buffers and drained when
we grant the credits to the peer.

This fixes regression Namjae reported with
the 6.18 release.

## References
- https://git.kernel.org/stable/c/26ad87a2cfb8c1384620d1693a166ed87303046e
- https://git.kernel.org/stable/c/66c082e3d4651e8629a393a9e182b01eb50fb0a3
- https://git.kernel.org/stable/c/809cbd31aa4f87a1b889532244c9cf30eb022385
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31538.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31538
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
