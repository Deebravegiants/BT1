# [C] BISHENG Authenticated Arbitrary Python Code Execution via Workflow run_once

## Summary
Severity: Critical
Advisory: CVE-2026-82278
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82278
Type: osv

## Details
BISHENG before 2.6.0 contains a remote code execution vulnerability in the workflow run_once endpoint that allows authenticated users to execute arbitrary Python code. Attackers can submit crafted Code node definitions to the POST /api/v1/workflow/run_once endpoint, which executes them with exec() without sandboxing, gaining access to filesystem, credentials, and internal network resources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82278.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82278
- https://www.vulncheck.com/advisories/bisheng-authenticated-arbitrary-python-code-execution-via-workflow-run-once
- https://github.com/dataelement/bisheng/issues/2189
- https://github.com/dataelement/bisheng
- https://github.com/dataelement/bisheng/blob/v2.4.0/src/backend/bisheng/api/services/workflow.py
