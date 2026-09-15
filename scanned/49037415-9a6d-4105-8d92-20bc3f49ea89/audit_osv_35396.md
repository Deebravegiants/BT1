# [H] picklescan - Arbitrary Code Execution via torch.fx.experimental.symbolic_shapes.ShapeEnv.evaluate_guards_expression

## Summary
Severity: High
Advisory: CVE-2025-71356
Aliases: GHSA-f4x7-rfwp-v3xw
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2025-71356
Type: osv

## Details
picklescan before 0.0.28 fails to detect malicious torch.fx.experimental.symbolic_shapes.ShapeEnv.evaluate_guards_expression function calls in pickle files. Attackers can embed undetected code in pickle files that executes remote code when loaded by victims.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71356.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-f4x7-rfwp-v3xw
- https://nvd.nist.gov/vuln/detail/CVE-2025-71356
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-torch-fx-experimental-symbolic-shapes-shapeenv-evaluate-guards-expression
