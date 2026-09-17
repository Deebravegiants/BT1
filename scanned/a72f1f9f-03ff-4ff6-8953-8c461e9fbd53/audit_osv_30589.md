# [H] clk: clk-loongson2: Fix memory corruption bug in struct loongson2_clk_provider

## Summary
Severity: High
Advisory: CVE-2024-53193
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53193
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: clk-loongson2: Fix memory corruption bug in struct loongson2_clk_provider

Some heap space is allocated for the flexible structure `struct
clk_hw_onecell_data` and its flexible-array member `hws` through
the composite structure `struct loongson2_clk_provider` in function
`loongson2_clk_probe()`, as shown below:

289         struct loongson2_clk_provider *clp;
	...
296         for (p = data; p->name; p++)
297                 clks_num++;
298
299         clp = devm_kzalloc(dev, struct_size(clp, clk_data.hws, clks_num),
300                            GFP_KERNEL);

Then some data is written into the flexible array:

350                 clp->clk_data.hws[p->id] = hw;

This corrupts `clk_lock`, which is the spinlock variable immediately
following the `clk_data` member in `struct loongson2_clk_provider`:

struct loongson2_clk_provider {
	void __iomem *base;
	struct device *dev;
	struct clk_hw_onecell_data clk_data;
	spinlock_t clk_lock;	/* protect access to DIV registers */
};

The problem is that the flexible structure is currently placed in the
middle of `struct loongson2_clk_provider` instead of at the end.

Fix this by moving `struct clk_hw_onecell_data clk_data;` to the end of
`struct loongson2_clk_provider`. Also, add a code comment to help
prevent this from happening again in case new members are added to the
structure in the future.

This change also fixes the following -Wflex-array-member-not-at-end
warning:

drivers/clk/clk-loongson2.c:32:36: warning: structure containing a flexible array member is not at the end of another structure [-Wflex-array-member-not-at-end]

## References
- https://git.kernel.org/stable/c/145de18065b9840687d9b4e63746238c1da25d22
- https://git.kernel.org/stable/c/6e4bf018bb040955da53dae9f8628ef8fcec2dbe
- https://git.kernel.org/stable/c/76918202615f2ba7deda14901d9fff528a180099
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53193.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53193
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
