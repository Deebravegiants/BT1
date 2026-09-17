# [H] udf: Fix bogus checksum computation in udf_rename()

## Summary
Severity: High
Advisory: CVE-2024-43845
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-43845
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: Fix bogus checksum computation in udf_rename()

Syzbot reports uninitialized memory access in udf_rename() when updating
checksum of '..' directory entry of a moved directory. This is indeed
true as we pass on-stack diriter.fi to the udf_update_tag() and because
that has only struct fileIdentDesc included in it and not the impUse or
name fields, the checksumming function is going to checksum random stack
contents beyond the end of the structure. This is actually harmless
because the following udf_fiiter_write_fi() will recompute the checksum
from on-disk buffers where everything is properly included. So all that
is needed is just removing the bogus calculation.

## References
- https://git.kernel.org/stable/c/27ab33854873e6fb958cb074681a0107cc2ecc4c
- https://git.kernel.org/stable/c/40d7b3ed52449d36143bab8d3e70926aa61a60f4
- https://git.kernel.org/stable/c/9c439311c13fc6faab1921441165c9b8b500c83b
- https://git.kernel.org/stable/c/fe2ead240c31e8d158713beca9d0681a6e6a53ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43845.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43845
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
