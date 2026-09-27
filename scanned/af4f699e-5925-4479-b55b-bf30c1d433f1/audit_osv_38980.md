# [H] smb: client: prevent races in ->query_interfaces()

## Summary
Severity: High
Advisory: CVE-2026-43239
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43239
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: prevent races in ->query_interfaces()

It was possible for two query interface works to be concurrently trying
to update the interfaces.

Prevent this by checking and updating iface_last_update under
iface_lock.

## References
- https://git.kernel.org/stable/c/6287eefaf21ec805d42f941bd368018cf397a7f5
- https://git.kernel.org/stable/c/76cc4faba0343c6db945b8dc75425b33d633e1b8
- https://git.kernel.org/stable/c/93e8e3ee165ae4609a1222b516b573837103d2c3
- https://git.kernel.org/stable/c/ab6564f416a6eaf1199200b6100952407b438f7d
- https://git.kernel.org/stable/c/c3c06e42e1527716c54f3ad2ced6a034b5f3a489
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43239.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43239
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
