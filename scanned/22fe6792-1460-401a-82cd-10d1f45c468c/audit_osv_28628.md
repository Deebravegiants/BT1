# [M] net: ll_temac: platform_get_resource replaced by wrong function

## Summary
Severity: Medium
Advisory: CVE-2024-35796
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35796
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ll_temac: platform_get_resource replaced by wrong function

The function platform_get_resource was replaced with
devm_platform_ioremap_resource_byname and is called using 0 as name.

This eventually ends up in platform_get_resource_byname in the call
stack, where it causes a null pointer in strcmp.

	if (type == resource_type(r) && !strcmp(r->name, name))

It should have been replaced with devm_platform_ioremap_resource.

## References
- https://git.kernel.org/stable/c/3a38a829c8bc27d78552c28e582eb1d885d07d11
- https://git.kernel.org/stable/c/46efbdbc95a30951c2579caf97b6df2ee2b3bef3
- https://git.kernel.org/stable/c/476eed5f1c22034774902a980aa48dc4662cb39a
- https://git.kernel.org/stable/c/553d294db94b5f139378022df480a9fb6c3ae39e
- https://git.kernel.org/stable/c/6d9395ba7f85bdb7af0b93272e537484ecbeff48
- https://git.kernel.org/stable/c/7e9edb569fd9f688d887e36db8170f6e22bafbc8
- https://git.kernel.org/stable/c/92c0c29f667870f17c0b764544bdf22ce0e886a1
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35796.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35796
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
