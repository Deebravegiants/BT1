# [H] Rhai stack overflow vulenrability

## Summary
Severity: High
Advisory: GHSA-67fv-9r7g-432h
CVE: CVE-2024-36760
CWE: CWE-120, CWE-674
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-13
Source: https://github.com/advisories/GHSA-67fv-9r7g-432h
Type: github-advisory

## Affected
- crates.io: `rhai` — affected >=0

## Details
A stack overflow vulnerability was found in version 1.18.0 of rhai. The flaw position is: (/ SRC/rhai/SRC/eval/STMT. Rs in rhai: : eval: : STMT: : _ $LT $impl $u20 $rhai.. engine.. Engine$GT$::eval_stmt::h3f1d68ce37fc6e96). Due to the stack overflow is a recursive call/SRC/rhai/SRC/eval/STMT. Rs file eval_stmt_block function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36760
- https://github.com/rhaiscript/rhai/commit/308d07a11d3bff0d230f685a6320292181e5a445
- https://github.com/MageWeiG/VulnerabilityCollection/blob/main/CVE-2024-36760/info.md
- https://github.com/rhaiscript/rhai
