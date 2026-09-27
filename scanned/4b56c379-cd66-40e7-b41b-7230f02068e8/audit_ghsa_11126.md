# [H] NLTK has Arbitrary File Read via Absolute Path Input in nltk.util.filestring()

## Summary
Severity: High
Advisory: GHSA-h8wq-7xc4-p3qx
CVE: CVE-2026-0846
CWE: CWE-36
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-h8wq-7xc4-p3qx
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.9.3

## Details
A vulnerability in the `filestring()` function of the `nltk.util` module in nltk version 3.9.2 allows arbitrary file read due to improper validation of input paths. The function directly opens files specified by user input without sanitization, enabling attackers to access sensitive system files by providing absolute paths or traversal paths. This vulnerability can be exploited locally or remotely, particularly in scenarios where the function is used in web APIs or other interfaces that accept user-supplied input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0846
- https://github.com/nltk/nltk/pull/3485
- https://github.com/nltk/nltk/commit/b2e1164bf89277f79b65406c829b99fb20ca1974
- https://github.com/nltk/nltk
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2026-97.yaml
- https://huntr.com/bounties/007b84f8-418e-4300-99d0-bf504c2f97eb
