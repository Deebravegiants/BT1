# [H] Bluetooth: ISO: lock sk in iso_connect_ind

## Summary
Severity: High
Advisory: CVE-2026-74538
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74538
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: lock sk in iso_connect_ind

Accessing iso_pi(sk)->conn requires lock_sock, which is not taken in the
"ev3" part of iso_connect_ind.  It may also be NULL if socket has
transitioned away from the LISTEN/CONNECT states before locking.

Fix by adding lock/release. Recheck hcon is valid after lock acquire
where needed.

## References
- https://git.kernel.org/stable/c/4311fd6f429065a8ba208660360a895627a00cf3
- https://git.kernel.org/stable/c/9bee7e476534f27e830658dad962d85da9edf6bf
- https://git.kernel.org/stable/c/e8e9cff6d80eeec28dec4cf7cc18662986945391
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74538.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74538
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
