# [H] virtio-net: ensure the received length does not exceed allocated size

## Summary
Severity: High
Advisory: CVE-2025-38375
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38375
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.189, >=5.16.0 <6.1.144, >=6.2.0 <6.6.97, >=6.7.0 <6.12.37, >=6.13.0 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio-net: ensure the received length does not exceed allocated size

In xdp_linearize_page, when reading the following buffers from the ring,
we forget to check the received length with the true allocate size. This
can lead to an out-of-bound read. This commit adds that missing check.

## References
- https://git.kernel.org/stable/c/11f2d0e8be2b5e784ac45fa3da226492c3e506d8
- https://git.kernel.org/stable/c/315dbdd7cdf6aa533829774caaf4d25f1fd20e73
- https://git.kernel.org/stable/c/6aca3dad2145e864dfe4d1060f45eb1bac75dd58
- https://git.kernel.org/stable/c/773e95c268b5d859f51f7547559734fd2a57660c
- https://git.kernel.org/stable/c/80b971be4c37a4d23a7f1abc5ff33dc7733d649b
- https://git.kernel.org/stable/c/982beb7582c193544eb9c6083937ec5ac1c9d651
- https://git.kernel.org/stable/c/bc68bc3563344ccdc57d1961457cdeecab8f81ef
- https://git.kernel.org/stable/c/ddc8649d363141fb3371dd81a73e1cb4ef8ed1e1
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38375.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38375
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
