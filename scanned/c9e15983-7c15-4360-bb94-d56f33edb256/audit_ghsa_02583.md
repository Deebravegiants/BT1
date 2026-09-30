# [H] NLTK Vulnerable to REDoS

## Summary
Severity: High
Advisory: GHSA-2ww3-fxvq-293j
CVE: CVE-2021-3828
CWE: CWE-1333, CWE-697
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-29
Source: https://github.com/advisories/GHSA-2ww3-fxvq-293j
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.6.4

## Details
The nltk package is vulnerable to ReDoS (regular expression denial of service). An attacker that is able to provide as an input to the [`_read_comparison_block()`(https://github.com/nltk/nltk/blob/23f4b1c4b4006b0cb3ec278e801029557cec4e82/nltk/corpus/reader/comparative_sents.py#L259) function in the file `nltk/corpus/reader/comparative_sents.py` may cause an application to consume an excessive amount of CPU.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3828
- https://github.com/nltk/nltk/pull/2816
- https://github.com/nltk/nltk/commit/277711ab1dec729e626b27aab6fa35ea5efbd7e6
- https://github.com/advisories/GHSA-2ww3-fxvq-293j
- https://github.com/nltk/nltk
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2021-356.yaml
- https://huntr.dev/bounties/d19aed43-75bc-4a03-91a0-4d0bb516bc32
