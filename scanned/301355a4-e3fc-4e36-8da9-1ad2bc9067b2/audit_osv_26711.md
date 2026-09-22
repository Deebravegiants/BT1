# [H] nvme-tcp: don't access released socket during error recovery

## Summary
Severity: High
Advisory: CVE-2023-53643
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53643
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-tcp: don't access released socket during error recovery

While the error recovery work is temporarily failing reconnect attempts,
running the 'nvme list' command causes a kernel NULL pointer dereference
by calling getsockname() with a released socket.

During error recovery work, the nvme tcp socket is released and a new one
created, so it is not safe to access the socket without proper check.

## References
- https://git.kernel.org/stable/c/76d54bf20cdcc1ed7569a89885e09636e9a8d71d
- https://git.kernel.org/stable/c/d82f762db4776fa11de88018f0f5de2d5db72a72
- https://git.kernel.org/stable/c/fe2d9e54165dadaa0d0cc3355c0be9c3e129fa0d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53643.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53643
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
