# [H] netfilter: nft_socket: fix sk refcount leaks

## Summary
Severity: High
Advisory: CVE-2024-46855
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46855
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.168, >=5.16.0 <6.1.111, >=6.2.0 <6.6.52, >=6.7.0 <6.10.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_socket: fix sk refcount leaks

We must put 'sk' reference before returning.

## References
- https://git.kernel.org/stable/c/076d281e90aaf4192799ecb9a1ed82321e133ecd
- https://git.kernel.org/stable/c/1f68e097e20d3c695281a9c6433acc37be47fe11
- https://git.kernel.org/stable/c/33c2258bf8cb17fba9e58b111d4c4f4cf43a4896
- https://git.kernel.org/stable/c/6572440f78b724c46070841a68254ebc534cde24
- https://git.kernel.org/stable/c/83e6fb59040e8964888afcaa5612cc1243736715
- https://git.kernel.org/stable/c/8b26ff7af8c32cb4148b3e147c52f9e4c695209c
- https://git.kernel.org/stable/c/ddc7c423c4a5386bf865474c694b48178efd311a
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46855.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46855
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
