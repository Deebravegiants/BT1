# [M] CVE-2021-47234

## Summary
Severity: Medium
Advisory: CVE-2021-47234
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47234
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

phy: phy-mtk-tphy: Fix some resource leaks in mtk_phy_init()

Use clk_disable_unprepare() in the error path of mtk_phy_init() to fix
some resource leaks.

## References
- https://git.kernel.org/stable/c/6472955af5e88b5489b6d78316082ad56ea3e489
- https://git.kernel.org/stable/c/9a17907946232d01aa2ec109da5f93b8d31dd425
- https://git.kernel.org/stable/c/aaac9a1bd370338ce372669eb9a6059d16b929aa
