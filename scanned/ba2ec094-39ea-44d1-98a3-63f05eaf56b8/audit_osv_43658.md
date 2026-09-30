# [H] Bluetooth: ISO: lock sk in iso_sock_getname

## Summary
Severity: High
Advisory: CVE-2026-74539
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74539
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: lock sk in iso_sock_getname

Accessing iso_pi(sk)->conn requires lock_sock, which is not held here.

Fix by adding the lock/release.

## References
- https://git.kernel.org/stable/c/202670e6602e068558c1fca2df40719ee91a2906
- https://git.kernel.org/stable/c/72d5bb1d77d7c3330146dc0cfd43f704c64b9594
- https://git.kernel.org/stable/c/89cf154d7c18e6e94a3da83051f3cf2bac317ae2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74539.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74539
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
