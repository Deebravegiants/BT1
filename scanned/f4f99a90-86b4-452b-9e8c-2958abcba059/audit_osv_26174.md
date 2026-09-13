# [H] CVE-2023-52340

## Summary
Severity: High
Advisory: CVE-2023-52340
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2023-52340
Type: osv

## Details
The IPv6 implementation in the Linux kernel before 6.3 has a net/ipv6/route.c max_size threshold that can be consumed easily, e.g., leading to a denial of service (network is unreachable errors) when IPv6 packets are sent in a loop via a raw socket.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit?id=af6d10345ca76670c1b7c37799f0d5576ccef277
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52340.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52340
- https://security.netapp.com/advisory/ntap-20240816-0005/
