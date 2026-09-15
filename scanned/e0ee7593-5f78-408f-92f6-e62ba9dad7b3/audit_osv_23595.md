# [M] net: sparx5: switchdev: fix possible NULL pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2022-49184
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49184
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sparx5: switchdev: fix possible NULL pointer dereference

As the possible failure of the allocation, devm_kzalloc() may return NULL
pointer.
Therefore, it should be better to check the 'db' in order to prevent
the dereference of NULL pointer.

## References
- https://git.kernel.org/stable/c/0906f3a3df07835e37077d8971aac65347f2ed57
- https://git.kernel.org/stable/c/b375ea083fa649092cd016ac1f89a2d1fd8f8e8b
- https://git.kernel.org/stable/c/c346791877e6ce923bb21e34b30c6f99326aa5a8
- https://git.kernel.org/stable/c/e7e1fff76c4c57688dc7d53a3b6212182d5628d0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49184.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49184
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
