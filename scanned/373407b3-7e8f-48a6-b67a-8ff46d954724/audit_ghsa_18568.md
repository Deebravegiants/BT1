# [M] Transformers's ReDoS vulnerability in get_configuration_file can lead to catastrophic backtracking

## Summary
Severity: Medium
Advisory: GHSA-q2wp-rjmx-x6x9
CVE: CVE-2025-3263
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-07-07
Source: https://github.com/advisories/GHSA-q2wp-rjmx-x6x9
Type: github-advisory

## Affected
- PyPI: `transformers` — affected >=0 <4.51.0

## Details
A Regular Expression Denial of Service (ReDoS) vulnerability was discovered in the Hugging Face Transformers library, specifically in the `get_configuration_file()` function within the `transformers.configuration_utils` module. The affected version is 4.49.0, and the issue is resolved in version 4.51.0. The vulnerability arises from the use of a regular expression pattern `config\.(.*)\.json` that can be exploited to cause excessive CPU consumption through crafted input strings, leading to catastrophic backtracking. This can result in model serving disruption, resource exhaustion, and increased latency in applications using the library.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3263
- https://github.com/huggingface/transformers/commit/0720e206c6ba28887e4d60ef60a6a089f6c1cc76
- https://github.com/huggingface/transformers/commit/126abe3461762e5fc180e7e614391d1b4ab051ca
- https://github.com/huggingface/transformers
- https://huntr.com/bounties/c7a69150-54f8-4e81-8094-791e7a2a0f29
