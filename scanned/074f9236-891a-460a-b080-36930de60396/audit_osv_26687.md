# [H] clk: imx: scu: use _safe list iterator to avoid a use after free

## Summary
Severity: High
Advisory: CVE-2023-53572
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53572
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: imx: scu: use _safe list iterator to avoid a use after free

This loop is freeing "clk" so it needs to use list_for_each_entry_safe().
Otherwise it dereferences a freed variable to get the next item on the
loop.

## References
- https://git.kernel.org/stable/c/08cc7cd2c2a29a2abf5bceb8f048c0734d3694ba
- https://git.kernel.org/stable/c/0a719f0e4b6f233979e219baff73923e76a96e09
- https://git.kernel.org/stable/c/3d90921f91fc6a8c801d527bb5848c99e335c1cf
- https://git.kernel.org/stable/c/632c60ecd25dbacee54d5581fe3aeb834b57010a
- https://git.kernel.org/stable/c/f95ff838ac39f861d1f95a0f3bbb1e01c2517d79
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53572.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53572
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
