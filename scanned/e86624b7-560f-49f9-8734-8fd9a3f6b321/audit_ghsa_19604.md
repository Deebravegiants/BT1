# [M] LlamaIndex Uncontrolled Resource Consumption vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jvpf-xf32-2w4q
CVE: CVE-2024-12910
CWE: CWE-400, CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-jvpf-xf32-2w4q
Type: github-advisory

## Affected
- PyPI: `llama-index` — affected >=0 <0.12.9

## Details
A vulnerability in the `KnowledgeBaseWebReader` class of the run-llama/llama_index repository, version latest, allows an attacker to cause a Denial of Service (DoS) by controlling a URL variable to contain the root URL. This leads to infinite recursive calls to the `get_article_urls` method, exhausting system resources and potentially crashing the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12910
- https://github.com/run-llama/llama_index/commit/159ce485a1168100bb219dc1b93133f1121579d9
- https://github.com/pypa/advisory-database/tree/main/vulns/llama-index/PYSEC-2025-11.yaml
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/27883f22-35ff-49df-aaa5-05031c7d6ad8
