# [H] tls: handle data disappearing from under the TLS ULP

## Summary
Severity: High
Advisory: CVE-2025-38616
Aliases: A-440544812, ASB-A-440544812
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38616
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.185, >=6.2.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: handle data disappearing from under the TLS ULP

TLS expects that it owns the receive queue of the TCP socket.
This cannot be guaranteed in case the reader of the TCP socket
entered before the TLS ULP was installed, or uses some non-standard
read API (eg. zerocopy ones). Replace the WARN_ON() and a buggy
early exit (which leaves anchor pointing to a freed skb) with real
error handling. Wipe the parsing state and tell the reader to retry.

We already reload the anchor every time we (re)acquire the socket lock,
so the only condition we need to avoid is an out of bounds read
(not having enough bytes in the socket for previously parsed record len).

If some data was read from under TLS but there's enough in the queue
we'll reload and decrypt what is most likely not a valid TLS record.
Leading to some undefined behavior from TLS perspective (corrupting
a stream? missing an alert? missing an attack?) but no kernel crash
should take place.

## References
- https://git.kernel.org/stable/c/2fb97ed9e2672b4f6e24ce206ac1a875ce4bcb38
- https://git.kernel.org/stable/c/6db015fc4b5d5f63a64a193f65d98da3a7fc811d
- https://git.kernel.org/stable/c/db3658a12d5ec4db7185ae7476151a50521b7207
- https://git.kernel.org/stable/c/eb0336f213fe88bbdb7d2b19c9c9ec19245a3155
- https://git.kernel.org/stable/c/ef50eaab631f9bf519ddbdfa42ccb0528adc1fc8
- https://git.kernel.org/stable/c/f1fe99919f629f980d0b8a7ff16950bffe06a859
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38616.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38616
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
