# [H] LlamaIndex has an XML Entity Expansion vulnerability in its sitemap parser

## Summary
Severity: High
Advisory: GHSA-w42r-mrx7-c633
CVE: CVE-2025-3225
CWE: CWE-776
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-07-07
Source: https://github.com/advisories/GHSA-w42r-mrx7-c633
Type: github-advisory

## Affected
- PyPI: `llama-index-readers-papers` — affected >=0 <0.3.2

## Details
An XML Entity Expansion vulnerability, also known as a 'billion laughs' attack, exists in the sitemap parser of the run-llama/llama_index repository, specifically affecting the Papers Loaders package before version 0.3.2 (in llama-index v0.10.0 and above through v0.12.29). This vulnerability allows an attacker to supply a malicious Sitemap XML, leading to a Denial of Service (DoS) by exhausting system memory and potentially causing a system crash. The issue is resolved in version 0.3.2 (in llama-index 0.12.29).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3225
- https://github.com/run-llama/llama_index/commit/4f6ee062b19212106a2632af9c9521fc7f0a3584
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/e33c0699-e9a2-49aa-837b-5363205637a2
