# [H] ASoC: simple-card-utils: Don't use __free(device_node) at graph_util_parse_dai()

## Summary
Severity: High
Advisory: CVE-2025-39930
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-39930
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.135, >=6.7.0 <6.12.82, >=6.13.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: simple-card-utils: Don't use __free(device_node) at graph_util_parse_dai()

commit 419d1918105e ("ASoC: simple-card-utils: use __free(device_node) for
device node") uses __free(device_node) for dlc->of_node, but we need to
keep it while driver is in use.

Don't use __free(device_node) in graph_util_parse_dai().

## References
- https://git.kernel.org/stable/c/146e25625378f7d4463acbd1ffbd975f3332a806
- https://git.kernel.org/stable/c/16a49e3fda339aa552cde7f2cdbb25b91426cb8a
- https://git.kernel.org/stable/c/232a32e8a7e9be8a2ee238df9b5304eed2f4e195
- https://git.kernel.org/stable/c/de74ec718e0788e1998eb7289ad07970e27cae27
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39930.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39930
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
