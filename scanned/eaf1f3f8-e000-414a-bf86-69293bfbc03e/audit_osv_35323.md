# [M] CVE-2025-71008

## Summary
Severity: Medium
Advisory: CVE-2025-71008
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2025-71008
Type: osv

## Details
A segmentation violation in the oneflow._oneflow_internal.autograd.Function.FunctionCtx.mark_non_differentiable component of OneFlow v0.9.0 allows attackers to cause a Denial of Service (DoS) via a crafted input.

## References
- https://github.com/Daisy2ang
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71008.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71008
- https://github.com/Oneflow-Inc/oneflow/issues/10651
