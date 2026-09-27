# [M] amt: fix possible memory leak in amt_rcv()

## Summary
Severity: Medium
Advisory: CVE-2022-49369
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49369
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

amt: fix possible memory leak in amt_rcv()

If an amt receives packets and it finds socket.
If it can't find a socket, it should free a received skb.
But it doesn't.
So, a memory leak would possibly occur.

## References
- https://git.kernel.org/stable/c/1a1a0e80e005cbdc2c250fc858e1d8570f4e4acb
- https://git.kernel.org/stable/c/4b8032d39b276c52db57ff834c300405b9da2691
- https://git.kernel.org/stable/c/60d9c020c69977e138727b3577bc6a0458325e9c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49369.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49369
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
