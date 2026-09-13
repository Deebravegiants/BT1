# [M] clk: samsung: Fix UBSAN panic in samsung_clk_init()

## Summary
Severity: Medium
Advisory: CVE-2025-39728
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-39728
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: samsung: Fix UBSAN panic in samsung_clk_init()

With UBSAN_ARRAY_BOUNDS=y, I'm hitting the below panic due to
dereferencing `ctx->clk_data.hws` before setting
`ctx->clk_data.num = nr_clks`. Move that up to fix the crash.

  UBSAN: array index out of bounds: 00000000f2005512 [#1] PREEMPT SMP
  <snip>
  Call trace:
   samsung_clk_init+0x110/0x124 (P)
   samsung_clk_init+0x48/0x124 (L)
   samsung_cmu_register_one+0x3c/0xa0
   exynos_arm64_register_cmu+0x54/0x64
   __gs101_cmu_top_of_clk_init_declare+0x28/0x60
   ...

## References
- https://git.kernel.org/stable/c/00307934eb94aaa0a99addfb37b9fe206f945004
- https://git.kernel.org/stable/c/0fef48f4a70e45a93e73c39023c3a6ea624714d6
- https://git.kernel.org/stable/c/157de9e48007a20c65d02fc0229a16f38134a72d
- https://git.kernel.org/stable/c/24307866e0ac0a5ddb462e766ceda5e27a6fbbe3
- https://git.kernel.org/stable/c/4d29a6dcb51e346595a15b49693eeb728925ca43
- https://git.kernel.org/stable/c/a1500b98cd81a32fdfb9bc63c33bb9f0c2a0a1bf
- https://git.kernel.org/stable/c/d19d7345a7bcdb083b65568a11b11adffe0687af
- https://git.kernel.org/stable/c/d974e177369c034984cece9d7d4fada9f8b9c740
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39728.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39728
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
