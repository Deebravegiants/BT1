# [M] gpio: grgpio: Add NULL check in grgpio_probe

## Summary
Severity: Medium
Advisory: CVE-2024-56634
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56634
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpio: grgpio: Add NULL check in grgpio_probe

devm_kasprintf() can return a NULL pointer on failure,but this
returned value in grgpio_probe is not checked.
Add NULL check in grgpio_probe, to handle kernel NULL
pointer dereference error.

## References
- https://git.kernel.org/stable/c/050b23d081da0f29474de043e9538c1f7a351b3b
- https://git.kernel.org/stable/c/09adf8792b61c09ae543972a1ece1884ef773848
- https://git.kernel.org/stable/c/4733f68e59bb7b9e3d395699abb18366954b9ba7
- https://git.kernel.org/stable/c/53ff0caa6ad57372d426b4f48fc0f66df43a731f
- https://git.kernel.org/stable/c/8d2ca6ac3711a4f4015d26b7cc84f325ac608edb
- https://git.kernel.org/stable/c/ad4dfa7ea7f5f7e9a3c78627cfc749bc7005ca7a
- https://git.kernel.org/stable/c/db2fc255fcf41f536ac8666409849e11659af88d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56634.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56634
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
