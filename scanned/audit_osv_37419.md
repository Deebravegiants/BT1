# [H] smb: smbdirect: introduce smbdirect_socket.recv_io.credits.available

## Summary
Severity: High
Advisory: CVE-2026-31539
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31539
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.11, >=6.19.0 <6.19.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: smbdirect: introduce smbdirect_socket.recv_io.credits.available

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

## References
- https://git.kernel.org/stable/c/6e3c5052f9686192e178806e017b7377155f4bab
- https://git.kernel.org/stable/c/e811e60e1cc79923c4388146eb1fa26a7482731e
- https://git.kernel.org/stable/c/f99996870222b598914a1f49d7375dc23752c237
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31539.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31539
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
