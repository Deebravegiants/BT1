# [M] Tencent AI-Infra-Guard skill-scan Analysis Bypass via Excluded Python Bytecode

## Summary
Severity: Medium
Advisory: CVE-2026-84809
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84809
Type: osv

## Details
Tencent AI-Infra-Guard's skill-scan component excludes compiled Python bytecode files from analysis by hardcoding __pycache__ directories and .pyc/.pyo/.pyd extensions into skip lists across multiple scanning surfaces. Attackers can distribute skills with benign Python source files alongside malicious compiled bytecode that executes on import while the scanner reports a safe verdict, enabling code execution when operators install the skill.

## References
- https://pypi.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84809.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84809
- https://www.vulncheck.com/advisories/tencent-ai-infra-guard-skill-scan-analysis-bypass-via-excluded-python-bytecode
- https://github.com/Tencent/AI-Infra-Guard/issues/531
- https://github.com/Tencent/AI-Infra-Guard/commit/7e0f749e3c023e5c6ab7b32fe97b3f6f2e8aeb04
- https://github.com/Tencent/AI-Infra-Guard
- https://github.com/Tencent/AI-Infra-Guard/blob/v4.6.0/skill-scan/skill_scan/tools/dir/dir_actions.py
- https://github.com/Tencent/AI-Infra-Guard/blob/v4.6.0/skill-scan/skill_scan/utils/pre_scan.py
