# [H] net: ethernet: lantiq_etop: fix double free in detach

## Summary
Severity: High
Advisory: CVE-2024-41046
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41046
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.0.0 <4.19.318, >=4.20.0 <5.4.280, >=5.5.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.100, >=6.2.0 <6.6.41, >=6.7.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: lantiq_etop: fix double free in detach

The number of the currently released descriptor is never incremented
which results in the same skb being released multiple times.

## References
- https://git.kernel.org/stable/c/1a2db00a554cfda57c397cce79b2804bf9633fec
- https://git.kernel.org/stable/c/22b16618a80858b3a9d607708444426948cc4ae1
- https://git.kernel.org/stable/c/69ad5fa0ce7c548262e0770fc2b726fe7ab4f156
- https://git.kernel.org/stable/c/84aaaa796a19195fc59290154fef9aeb1fba964f
- https://git.kernel.org/stable/c/907443174e76b854d28024bd079f0e53b94dc9a1
- https://git.kernel.org/stable/c/9d23909ae041761cb2aa0c3cb1748598d8b6bc54
- https://git.kernel.org/stable/c/c2b66e2b3939af63699e4a4bd25a8ac4a9b1d1b3
- https://git.kernel.org/stable/c/e1533b6319ab9c3a97dad314dd88b3783bc41b69
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41046.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41046
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
