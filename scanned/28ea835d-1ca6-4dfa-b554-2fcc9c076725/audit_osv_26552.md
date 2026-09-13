# [M] media: ipu-bridge: Fix null pointer deref on SSDB/PLD parsing warnings

## Summary
Severity: Medium
Advisory: CVE-2023-53336
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53336
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: ipu-bridge: Fix null pointer deref on SSDB/PLD parsing warnings

When ipu_bridge_parse_rotation() and ipu_bridge_parse_orientation() run
sensor->adev is not set yet.

So if either of the dev_warn() calls about unknown values are hit this
will lead to a NULL pointer deref.

Set sensor->adev earlier, with a borrowed ref to avoid making unrolling
on errors harder, to fix this.

## References
- https://git.kernel.org/stable/c/284be5693163343e1cf17c03917eecd1d6681bcf
- https://git.kernel.org/stable/c/3de35e29cfddfe6bff762b15bcfe8d80bebac6cb
- https://git.kernel.org/stable/c/e08b091e33ecf6e4cb2c0c5820a69abe7673280b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53336.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53336
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
