# [H] Topydo Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-h6h9-pphv-m266
CVE: CVE-2018-1000523
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2018-09-13
Source: https://github.com/advisories/GHSA-h6h9-pphv-m266
Type: github-advisory

## Affected
- PyPI: `topydo` — affected >=0

## Details
topydo contains a CWE-20: Improper Input Validation vulnerability in `ListFormatParser::parse`, file `topydo/lib/ListFormat.py` line 292 as of d4f843dac71308b2f29a7c2cdc76f055c3841523 that can result in Injection of arbitrary bytes to the terminal, including terminal escape code sequences. This attack appear to be exploitable via The victim must open a todo.txt with at least one specially crafted line.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000523
- https://github.com/bram85/topydo/issues/240
- https://github.com/advisories/GHSA-h6h9-pphv-m266
- https://github.com/bram85/topydo
- https://github.com/bram85/topydo/blob/master/topydo/lib/ListFormat.py#L292
- https://github.com/pypa/advisory-database/tree/main/vulns/topydo/PYSEC-2018-76.yaml
