# [H] Bluetooth: ISO: Fix UAF on iso_sock_timeout

## Summary
Severity: High
Advisory: CVE-2024-50124
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50124
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: Fix UAF on iso_sock_timeout

conn->sk maybe have been unlinked/freed while waiting for iso_conn_lock
so this checks if the conn->sk is still valid by checking if it part of
iso_sk_list.

## References
- https://git.kernel.org/stable/c/14bcb721d241e62fdd18f6f434a2ed2ab6e71a9b
- https://git.kernel.org/stable/c/246b435ad668596aa0e2bbb9d491b6413861211a
- https://git.kernel.org/stable/c/876ac72d535fa94f4ac57bba651987c6f990f646
- https://git.kernel.org/stable/c/d75aad1d3143ca68cda52ff80ac392e1bbd84325
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50124.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50124
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
