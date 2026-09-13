# [H] batman-adv: dat: ensure accessible eth_hdr proto field

## Summary
Severity: High
Advisory: CVE-2026-80599
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80599
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: dat: ensure accessible eth_hdr proto field

When batadv_get_vid() accesses the proto field of the ethernet header, it
is not checking if the data itself is accessible. The caller is responsible
for it. But in contrast to other call sites, batadv_dat_get_vid() and its
caller didn't make sure this is true. This could have caused an
out-of-bounds access.

## References
- https://git.kernel.org/stable/c/26560c4a03dc4d607331600c187f59ab2df5f341
- https://git.kernel.org/stable/c/3c62694c31f043568c3f4784b8d247cc3bea6b4c
- https://git.kernel.org/stable/c/4407ff3af469356f9641c4a6e7072309bae86bea
- https://git.kernel.org/stable/c/5836a050d02e9598fa0f71e88dde28b63dfa35e3
- https://git.kernel.org/stable/c/6d3ea37074bb747f745d28138f87745ba9bd97c5
- https://git.kernel.org/stable/c/7913935d41f166c367bbf7cc76a79e50044388e8
- https://git.kernel.org/stable/c/8f76277d02176cd739945bba3379448e2e22e799
- https://git.kernel.org/stable/c/da3677b5ed362742d30ceab31bfafcdc74dc2642
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80599.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80599
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
