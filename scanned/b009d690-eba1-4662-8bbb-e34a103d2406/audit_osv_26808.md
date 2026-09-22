# [H] net: dsa: realtek: fix out-of-bounds access

## Summary
Severity: High
Advisory: CVE-2023-54065
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54065
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.23, >=6.2.0 <6.2.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: realtek: fix out-of-bounds access

The probe function sets priv->chip_data to (void *)priv + sizeof(*priv)
with the expectation that priv has enough trailing space.

However, only realtek-smi actually allocated this chip_data space.
Do likewise in realtek-mdio to fix out-of-bounds accesses.

These accesses likely went unnoticed so far, because of an (unused)
buf[4096] member in struct realtek_priv, which caused kmalloc to
round up the allocated buffer to a big enough size, so nothing of
value was overwritten. With a different allocator (like in the barebox
bootloader port of the driver) or with KASAN, the memory corruption
becomes quickly apparent.

## References
- https://git.kernel.org/stable/c/b93eb564869321d0dffaf23fcc5c88112ed62466
- https://git.kernel.org/stable/c/cc0f9bb99735d2b68fac68f37b585d615728ce5b
- https://git.kernel.org/stable/c/fe668aa499b4b95425044ba11af9609db6ecf466
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54065.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54065
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
