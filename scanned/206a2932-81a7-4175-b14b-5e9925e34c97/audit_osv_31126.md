# [H] KEYS: trusted: dcp: fix improper sg use with CONFIG_VMAP_STACK=y

## Summary
Severity: High
Advisory: CVE-2024-58008
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-58008
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

KEYS: trusted: dcp: fix improper sg use with CONFIG_VMAP_STACK=y

With vmalloc stack addresses enabled (CONFIG_VMAP_STACK=y) DCP trusted
keys can crash during en- and decryption of the blob encryption key via
the DCP crypto driver. This is caused by improperly using sg_init_one()
with vmalloc'd stack buffers (plain_key_blob).

Fix this by always using kmalloc() for buffers we give to the DCP crypto
driver.

## References
- https://git.kernel.org/stable/c/3192f1c54dddb9b5820bf5e8677809949d8e9c66
- https://git.kernel.org/stable/c/3355594de46fb1cba663f12b9644b664b8a609f4
- https://git.kernel.org/stable/c/e8d9fab39d1f87b52932646b2f1e7877aa3fc0f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58008.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58008
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
