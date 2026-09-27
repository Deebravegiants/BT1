# [H] clk: mediatek: Drop __initconst from gates

## Summary
Severity: High
Advisory: CVE-2026-45909
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45909
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: mediatek: Drop __initconst from gates

Since commit 8ceff24a754a ("clk: mediatek: clk-gate: Refactor
mtk_clk_register_gate to use mtk_gate struct") the mtk_gate structs
are no longer just used for initialization/registration, but also at
runtime. So drop __initconst annotations.

## References
- https://git.kernel.org/stable/c/1debd9ba7eb18af8fb63dc93517c6bbcab0e31ee
- https://git.kernel.org/stable/c/866d8ecc4e789f7d73d6cafd1b122d1b6032b3b1
- https://git.kernel.org/stable/c/871afb43e41ad4e8246438de495a939cd0f8113c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45909.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45909
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
