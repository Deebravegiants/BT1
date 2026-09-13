# [C] ipvs: reload ip header after head reallocation

## Summary
Severity: Critical
Advisory: CVE-2026-68476
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68476
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.269, >=5.11.0 <5.15.220, >=5.16.0 <6.1.187, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvs: reload ip header after head reallocation

__ip_vs_get_out_rt() calls skb_ensure_writable() which may
reallocate skb->head.

## References
- https://git.kernel.org/stable/c/3fb7edd2018bb1ad0a68157383d9b9dac33dd645
- https://git.kernel.org/stable/c/4f2d1151421520d7ae16ca8d367d0ca09f5dfbd7
- https://git.kernel.org/stable/c/657118cad620172dfd8f6ed5717fd75c0d1f7a5a
- https://git.kernel.org/stable/c/a10f5080afbed242640f2984328de25f84557da1
- https://git.kernel.org/stable/c/a2f57827bf7c695b8c72dc4511cae8e86582369d
- https://git.kernel.org/stable/c/ac6ac3d35bfc0ade9d17d354c84e503a946ebdab
- https://git.kernel.org/stable/c/ad1e14710b360bda087ebf9fb82460eb5ef775de
- https://git.kernel.org/stable/c/e51687fc56c2e39ea6e9532925f1aabd4d529f61
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68476.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68476
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
