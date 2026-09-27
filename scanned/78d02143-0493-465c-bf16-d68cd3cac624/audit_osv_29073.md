# [C] clk: bcm: dvp: Assign ->num before accessing ->hws

## Summary
Severity: Critical
Advisory: CVE-2024-39462
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-39462
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.34, >=6.7.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: bcm: dvp: Assign ->num before accessing ->hws

Commit f316cdff8d67 ("clk: Annotate struct clk_hw_onecell_data with
__counted_by") annotated the hws member of 'struct clk_hw_onecell_data'
with __counted_by, which informs the bounds sanitizer about the number
of elements in hws, so that it can warn when hws is accessed out of
bounds. As noted in that change, the __counted_by member must be
initialized with the number of elements before the first array access
happens, otherwise there will be a warning from each access prior to the
initialization because the number of elements is zero. This occurs in
clk_dvp_probe() due to ->num being assigned after ->hws has been
accessed:

  UBSAN: array-index-out-of-bounds in drivers/clk/bcm/clk-bcm2711-dvp.c:59:2
  index 0 is out of range for type 'struct clk_hw *[] __counted_by(num)' (aka 'struct clk_hw *[]')

Move the ->num initialization to before the first access of ->hws, which
clears up the warning.

## References
- https://git.kernel.org/stable/c/0dc913217fb79096597005bba9ba738e2db5cd02
- https://git.kernel.org/stable/c/9368cdf90f52a68120d039887ccff74ff33b4444
- https://git.kernel.org/stable/c/a1dd92fca0d6b58b55ed0484f75d4205dbb77010
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39462.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39462
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
