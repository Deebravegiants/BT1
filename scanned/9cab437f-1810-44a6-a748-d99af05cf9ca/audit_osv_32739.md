# [H] udmabuf: fix a buf size overflow issue during udmabuf creation

## Summary
Severity: High
Advisory: CVE-2025-37803
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-08
Source: https://osv.dev/vulnerability/CVE-2025-37803
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.293, >=5.5.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.136, >=6.2.0 <6.6.89, >=6.7.0 <6.12.57, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

udmabuf: fix a buf size overflow issue during udmabuf creation

by casting size_limit_mb to u64  when calculate pglimit.

## References
- https://git.kernel.org/stable/c/021ba7f1babd029e714d13a6bf2571b08af96d0f
- https://git.kernel.org/stable/c/13fe12c037b470321436deec393030c6153cfeb9
- https://git.kernel.org/stable/c/29b65a3171a49c9b69f31035146be966cec40b7a
- https://git.kernel.org/stable/c/2b8419c6ecf69007dcff54ea0b9f0b215282c55a
- https://git.kernel.org/stable/c/373512760e13fdaa726faa9502d0f5be2abb3d33
- https://git.kernel.org/stable/c/3f6c9d66e0f8eb9679b57913aa64b4d2266f6fbe
- https://git.kernel.org/stable/c/b2ff4e9c599b000833d16a917f519aa2e4a75de2
- https://git.kernel.org/stable/c/e84a08fc7e25cdad5d9a3def42cc770ff711193f
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37803.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37803
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
