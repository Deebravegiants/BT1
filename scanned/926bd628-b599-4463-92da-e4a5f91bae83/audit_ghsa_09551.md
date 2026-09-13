# [H] ModelScope is vulnerable to arbitrary code injection via a crafted module

## Summary
Severity: High
Advisory: GHSA-fhhq-h4hg-549x
CVE: CVE-2025-51427
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-fhhq-h4hg-549x
Type: github-advisory

## Affected
- PyPI: `modelscope` — affected >=0 <1.27.0

## Details
An issue was discovered in ModelScope 1.25.0 allowing attackers to execute arbitrary code via crafted module listed in the configuration file (dey_mini.yaml) under the key ['nnet']['module'].

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-51427
- https://github.com/modelscope/modelscope/issues/1331
- https://github.com/modelscope/modelscope/pull/1333
- https://github.com/modelscope/modelscope/commit/75d54927e112261d39598ca08c15b66a7ff3f735
- https://github.com/JIRUWOZHI/vulnerability-disclosure/blob/main/CVE-2025-51427/CVE_2025_51427.md
- https://github.com/modelscope/modelscope
