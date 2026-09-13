# [H] k8sGPT has Prompt Injection through its k8sGPT-Operator

## Summary
Severity: High
Advisory: GHSA-rp7v-4384-hfrp
CWE: CWE-20, CWE-502, CWE-915
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-rp7v-4384-hfrp
Type: github-advisory

## Affected
- Go: `github.com/k8sgpt-ai/k8sgpt` — affected >=0 <0.4.32

## Details
### Summary
In the auto-remediation pipeline, `object_to_execution.go` was deserializing the AI-generated YAML directly into a Deployment object, but there was lack of validation from the original Deployment object.

### Details
This issue was fixed after coordination with Alex Jones.

### PoC
To minimize the impact, the PoC of this vulnerability wasn't released, but was shared with the maintainers.

## References
- https://github.com/k8sgpt-ai/k8sgpt/security/advisories/GHSA-rp7v-4384-hfrp
- https://github.com/k8sgpt-ai/k8sgpt
