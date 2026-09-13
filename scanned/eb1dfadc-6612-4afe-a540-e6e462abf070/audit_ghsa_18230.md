# [M] Hugging Face Transformers is vulnerable to ReDoS through its MarianTokenizer

## Summary
Severity: Medium
Advisory: GHSA-59p9-h35m-wg4g
CVE: CVE-2025-6638
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-09-12
Source: https://github.com/advisories/GHSA-59p9-h35m-wg4g
Type: github-advisory

## Affected
- PyPI: `transformers` — affected >=0 <4.53.0

## Details
A Regular Expression Denial of Service (ReDoS) vulnerability was discovered in the Hugging Face Transformers library, specifically affecting the MarianTokenizer's `remove_language_code()` method. This vulnerability is present in version 4.52.4 and has been fixed in version 4.53.0. The issue arises from inefficient regex processing, which can be exploited by crafted input strings containing malformed language code patterns, leading to excessive CPU consumption and potential denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6638
- https://github.com/huggingface/transformers/commit/47c34fba5c303576560cb29767efb452ff12b8be
- https://github.com/huggingface/transformers/commit/d37f7517972f67e3f2194c000ed0f87f064e5099
- https://github.com/huggingface/transformers
- https://huntr.com/bounties/6a6c933f-9ce8-4ded-8b3b-2c1444c61f36
