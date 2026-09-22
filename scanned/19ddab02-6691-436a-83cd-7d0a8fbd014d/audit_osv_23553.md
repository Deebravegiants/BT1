# [H] scsi: libfc: Fix use after free in fc_exch_abts_resp()

## Summary
Severity: High
Advisory: CVE-2022-49114
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49114
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <4.9.311, >=4.10.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: libfc: Fix use after free in fc_exch_abts_resp()

fc_exch_release(ep) will decrease the ep's reference count. When the
reference count reaches zero, it is freed. But ep is still used in the
following code, which will lead to a use after free.

Return after the fc_exch_release() call to avoid use after free.

## References
- https://git.kernel.org/stable/c/1d7effe5fff9d28e45e18ac3a564067c7ddfe898
- https://git.kernel.org/stable/c/271add11994ba1a334859069367e04d2be2ebdd4
- https://git.kernel.org/stable/c/412dd8299b02e4410fe77b8396953c1a8dde183a
- https://git.kernel.org/stable/c/499d198494e77b6533251b9b909baf5c101129cb
- https://git.kernel.org/stable/c/4a131d4ea8b581ac9b01d3a72754db4848be3232
- https://git.kernel.org/stable/c/5cf2ce8967b0d98c8cfa4dc42ef4fcf080f5c836
- https://git.kernel.org/stable/c/6044ad64f41c87382cfeeca281573d1886d80cbe
- https://git.kernel.org/stable/c/87909291762d08fdb60d19069d7a89b5b308d0ef
- https://git.kernel.org/stable/c/f581df412bc45c95176e3c808ee2839c05b2ab0c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49114.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49114
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
