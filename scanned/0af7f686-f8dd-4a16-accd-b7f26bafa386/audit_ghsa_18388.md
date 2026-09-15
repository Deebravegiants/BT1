# [M] Transformers vulnerable to ReDoS attack through its get_imports() function

## Summary
Severity: Medium
Advisory: GHSA-jjph-296x-mrcr
CVE: CVE-2025-3264
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-07-07
Source: https://github.com/advisories/GHSA-jjph-296x-mrcr
Type: github-advisory

## Affected
- PyPI: `transformers` — affected >=0 <4.51.0

## Details
A Regular Expression Denial of Service (ReDoS) vulnerability was discovered in the Hugging Face Transformers library, specifically in the `get_imports()` function within `dynamic_module_utils.py`. This vulnerability affects versions 4.49.0 and is fixed in version 4.51.0. The issue arises from a regular expression pattern `\s*try\s*:.*?except.*?:` used to filter out try/except blocks from Python code, which can be exploited to cause excessive CPU consumption through crafted input strings due to catastrophic backtracking. This vulnerability can lead to remote code loading disruption, resource exhaustion in model serving, supply chain attack vectors, and development pipeline disruption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3264
- https://github.com/huggingface/transformers/commit/0720e206c6ba28887e4d60ef60a6a089f6c1cc76
- https://github.com/huggingface/transformers/commit/126abe3461762e5fc180e7e614391d1b4ab051ca
- https://github.com/huggingface/transformers
- https://huntr.com/bounties/3c6f7822-9992-476d-8cf0-b0b1623427df
