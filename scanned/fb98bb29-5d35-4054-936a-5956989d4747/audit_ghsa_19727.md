# [C] PlotAI eval vulnerability

## Summary
Severity: Critical
Advisory: GHSA-2hmp-5wqg-f24h
CVE: CVE-2025-1497
CWE: CWE-77, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-2hmp-5wqg-f24h
Type: github-advisory

## Affected
- PyPI: `plotai` — affected >=0 <0.0.7

## Details
A vulnerability, that could result in Remote Code Execution (RCE), has been found in PlotAI. Lack of validation of LLM-generated output allows attacker to execute arbitrary Python code. PlotAI commented out vulnerable line, further usage of the software requires uncommenting it and thus accepting the risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1497
- https://github.com/mljar/plotai/commit/bdcfb13484f0b85703a4c1ddfd71cb21840e7fde
- https://cert.pl/en/posts/2025/03/CVE-2025-1497
- https://cert.pl/posts/2025/03/CVE-2025-1497
- https://github.com/mljar/plotai
- https://github.com/pypa/advisory-database/tree/main/vulns/plotai/PYSEC-2025-22.yaml
