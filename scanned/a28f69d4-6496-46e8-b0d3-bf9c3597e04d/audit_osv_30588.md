# [H] clk: clk-loongson2: Fix potential buffer overflow in flexible-array member access

## Summary
Severity: High
Advisory: CVE-2024-53192
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53192
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: clk-loongson2: Fix potential buffer overflow in flexible-array member access

Flexible-array member `hws` in `struct clk_hw_onecell_data` is annotated
with the `counted_by()` attribute. This means that when memory is
allocated for this array, the _counter_, which in this case is member
`num` in the flexible structure, should be set to the maximum number of
elements the flexible array can contain, or fewer.

In this case, the total number of elements for the flexible array is
determined by variable `clks_num` when allocating heap space via
`devm_kzalloc()`, as shown below:

289         struct loongson2_clk_provider *clp;
	...
296         for (p = data; p->name; p++)
297                 clks_num++;
298
299         clp = devm_kzalloc(dev, struct_size(clp, clk_data.hws, clks_num),
300                            GFP_KERNEL);

So, `clp->clk_data.num` should be set to `clks_num` or less, and not
exceed `clks_num`, as is currently the case. Otherwise, if data is
written into `clp->clk_data.hws[clks_num]`, the instrumentation
provided by the compiler won't detect the overflow, leading to a
memory corruption bug at runtime.

Fix this issue by setting `clp->clk_data.num` to `clks_num`.

## References
- https://git.kernel.org/stable/c/02fb4f0084331ef72c28d0c70fcb15d1bea369ec
- https://git.kernel.org/stable/c/1bf8877150128c3abd9d233886a05f6966fbf0c7
- https://git.kernel.org/stable/c/b96fc194984d0c82de1ca2b4166b35b1298b216c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53192.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53192
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
