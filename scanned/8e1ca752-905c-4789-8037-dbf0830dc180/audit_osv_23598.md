# [M] clk: Fix clk_hw_get_clk() when dev is NULL

## Summary
Severity: Medium
Advisory: CVE-2022-49187
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49187
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: Fix clk_hw_get_clk() when dev is NULL

Any registered clk_core structure can have a NULL pointer in its dev
field. While never actually documented, this is evidenced by the wide
usage of clk_register and clk_hw_register with a NULL device pointer,
and the fact that the core of_clk_hw_register() function also passes a
NULL device pointer.

A call to clk_hw_get_clk() on a clk_hw struct whose clk_core is in that
case will result in a NULL pointer derefence when it calls dev_name() on
that NULL device pointer.

Add a test for this case and use NULL as the dev_id if the device
pointer is NULL.

## References
- https://git.kernel.org/stable/c/0c1b56df451716ba207bbf59f303473643eee4fd
- https://git.kernel.org/stable/c/23f89fe005b105f0dcc55034c13eb89f9b570fac
- https://git.kernel.org/stable/c/4be3e4c05d8dd1b83b75652cad88c9e752ec7054
- https://git.kernel.org/stable/c/d183f20cf5a7b546d4108e796b98210ceb317579
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49187.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49187
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
