# [C] tls: separate no-async decryption request handling from async

## Summary
Severity: Critical
Advisory: CVE-2024-58240
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-28
Source: https://osv.dev/vulnerability/CVE-2024-58240
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.149, >=6.2.0 <6.6.21, >=6.7.0 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: separate no-async decryption request handling from async

If we're not doing async, the handling is much simpler. There's no
reference counting, we just need to wait for the completion to wake us
up and return its result.

We should preferably also use a separate crypto_wait. I'm not seeing a
UAF as I did in the past, I think aec7961916f3 ("tls: fix race between
async notify and socket close") took care of it.

This will make the next fix easier.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/41532b785e9d79636b3815a64ddf6a096647d011
- https://git.kernel.org/stable/c/48905146d11dbf1ddbb2967319016a83976953f5
- https://git.kernel.org/stable/c/5f7761c94b1db7570cab328c9f940a33284509b7
- https://git.kernel.org/stable/c/999115298017a675d8ddf61414fc7a85c89f1186
- https://git.kernel.org/stable/c/dec5b6e7b211e405d3bcb504562ab21aa7e5a64d
- https://git.kernel.org/stable/c/f32ab6cb544d01cdc150de5df389ac685aa507b0
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58240.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58240
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
