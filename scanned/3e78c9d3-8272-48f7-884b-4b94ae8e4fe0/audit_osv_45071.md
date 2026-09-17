# [H] PYSEC-2025-40

## Summary
Severity: High
Advisory: PYSEC-2025-40
Aliases: CVE-2025-2099, GHSA-qq3j-4f4f-9583
Ecosystem: PyPI
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-19
Source: https://osv.dev/vulnerability/PYSEC-2025-40
Type: osv

## Affected
- PyPI: `transformers` — affected >=0 <8cb522b4190bd556ce51be04942720650b1a3e57, >=0 <4.49.0

## Details
A vulnerability in the `preprocess_string()` function of the `transformers.testing_utils` module in huggingface/transformers version v4.48.3 allows for a Regular Expression Denial of Service (ReDoS) attack. The regular expression used to process code blocks in docstrings contains nested quantifiers, leading to exponential backtracking when processing input with a large number of newline characters. An attacker can exploit this by providing a specially crafted payload, causing high CPU usage and potential application downtime, effectively resulting in a Denial of Service (DoS) scenario.

## References
- https://huntr.com/bounties/97b780f3-ffca-424f-ad5d-0e1c57a5bde4
- https://github.com/huggingface/transformers/commit/8cb522b4190bd556ce51be04942720650b1a3e57
- https://huntr.com/bounties/97b780f3-ffca-424f-ad5d-0e1c57a5bde4
- https://github.com/advisories/GHSA-qq3j-4f4f-9583
