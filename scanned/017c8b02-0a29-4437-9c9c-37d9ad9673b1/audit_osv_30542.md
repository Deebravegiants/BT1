# [M] pmdomain: imx93-blk-ctrl: correct remove path

## Summary
Severity: Medium
Advisory: CVE-2024-53134
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-53134
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.6.63, >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

pmdomain: imx93-blk-ctrl: correct remove path

The check condition should be 'i < bc->onecell_data.num_domains', not
'bc->onecell_data.num_domains' which will make the look never finish
and cause kernel panic.

Also disable runtime to address
"imx93-blk-ctrl 4ac10000.system-controller: Unbalanced pm_runtime_enable!"

## References
- https://git.kernel.org/stable/c/201fb9e164a1e4c5937de2cf58bcb0327c08664f
- https://git.kernel.org/stable/c/8fc228ab5d38a026eae7183a5f74a4fac43d9b6a
- https://git.kernel.org/stable/c/f7c7c5aa556378a2c8da72c1f7f238b6648f95fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53134.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53134
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
