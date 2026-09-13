# [H] s390/dasd: fix Oops in dasd_alias_get_start_dev due to missing pavgroup

## Summary
Severity: High
Advisory: CVE-2022-48636
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-28
Source: https://osv.dev/vulnerability/CVE-2022-48636
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <4.9.330, >=4.10.0 <4.14.295, >=4.15.0 <4.19.260, >=4.20.0 <5.4.215, >=5.5.0 <5.10.146, >=5.11.0 <5.15.71, >=5.16.0 <5.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/dasd: fix Oops in dasd_alias_get_start_dev due to missing pavgroup

Fix Oops in dasd_alias_get_start_dev() function caused by the pavgroup
pointer being NULL.

The pavgroup pointer is checked on the entrance of the function but
without the lcu->lock being held. Therefore there is a race window
between dasd_alias_get_start_dev() and _lcu_update() which sets
pavgroup to NULL with the lcu->lock held.

Fix by checking the pavgroup pointer with lcu->lock held.

## References
- https://git.kernel.org/stable/c/2e473351400e3dd66f0b71eddcef82ee45a584c1
- https://git.kernel.org/stable/c/49f401a98b318761ca2e15d4c7869a20043fbed4
- https://git.kernel.org/stable/c/650a2e79d176db753654d3dde88e53a2033036ac
- https://git.kernel.org/stable/c/aaba5ff2742043705bc4c02fd0b2b246e2e16da1
- https://git.kernel.org/stable/c/d3a67c21b18f33c79382084af556557c442f12a6
- https://git.kernel.org/stable/c/d86b4267834e6d4af62e3073e48166e349ab1b70
- https://git.kernel.org/stable/c/db7ba07108a48c0f95b74fabbfd5d63e924f992d
- https://git.kernel.org/stable/c/f5fcc9d6d71d9ff7fdbdd4b89074e6e24fffc20b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48636.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48636
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
