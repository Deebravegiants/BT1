# [H] net/smc: Do not re-initialize smc hashtables

## Summary
Severity: High
Advisory: CVE-2026-64005
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64005
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: Do not re-initialize smc hashtables

INIT_HLIST_HEAD(&smc_v*_hashinfo.ht) are called after smc_nl_init(),
proto_register() and sock_register(). This can lead to smc_v*_hashinfo.ht
being reset even though hash entries already exist and are being used,
possibly resulting in a corrupted list.

Remove unnecessary and dangerous re-initialisation of smc_v*_hashinfo.ht in
smc_init(); it is implicitly initialised to zero anyhow. Add
HLIST_HEAD_INIT to the definitions for clarity.

## References
- https://git.kernel.org/stable/c/0cc9d0ac22d02f1ba1884de5d6de9eaf8b45d82d
- https://git.kernel.org/stable/c/2006605006e5a4a11d93e1ebdbbe95764d24276f
- https://git.kernel.org/stable/c/55cba6b883b41e5922c00ba9d4e3262131f46f1b
- https://git.kernel.org/stable/c/5ec939367e700722ffbb1b7cacccbb1a3cf0ebd1
- https://git.kernel.org/stable/c/64c96e497d5ada0b90e99bf58f893aa2b73dcfbc
- https://git.kernel.org/stable/c/9e4389b0038781f19f97895186ed941ff8ac1678
- https://git.kernel.org/stable/c/cdc79c05cc375f68ae87b0c74fdaac1a5c93155a
- https://git.kernel.org/stable/c/ed7a758313011885347b854e97cb95903ef3c3f7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64005.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64005
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
