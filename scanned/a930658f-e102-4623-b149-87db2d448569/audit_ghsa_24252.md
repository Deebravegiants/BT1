# [H] txAWS AWSServiceEndpoint defaults to not verifying server certificates

## Summary
Severity: High
Advisory: GHSA-cggm-52qp-wvw7
CVE: CVE-2017-1000007
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-cggm-52qp-wvw7
Type: github-advisory

## Affected
- PyPI: `txaws` — affected >=0 <0.4.0

## Details
txAWS fails to perform complete certificate verification resulting in vulnerability to MitM attacks and information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000007
- https://github.com/twisted/txaws/issues/24
- https://github.com/twisted/txaws/pull/26
- https://github.com/twisted/txaws/commit/46b66c3dc315de7b5896d60531311ec9658bc466
- https://github.com/pypa/advisory-database/tree/main/vulns/txaws/PYSEC-2017-85.yaml
- https://github.com/twisted/txaws
