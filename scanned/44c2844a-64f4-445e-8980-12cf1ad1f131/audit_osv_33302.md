# [H] ASoC: codecs: wcd937x: set the comp soundwire port correctly

## Summary
Severity: High
Advisory: CVE-2025-40045
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40045
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: codecs: wcd937x: set the comp soundwire port correctly

For some reason we endup with setting soundwire port for
HPHL_COMP and HPHR_COMP as zero, this can potentially result
in a memory corruption due to accessing and setting -1 th element of
port_map array.

## References
- https://git.kernel.org/stable/c/1a1ca38392e7e896075afc8905ddaea525ed30f7
- https://git.kernel.org/stable/c/66a940b1bf48a7095162688332d725ba160154eb
- https://git.kernel.org/stable/c/abcd537aae3b84c6d10ad147e99a204bcb56b234
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40045.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40045
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
