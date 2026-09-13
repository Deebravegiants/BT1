# [H] Setuptools vulnerable to Man-in-the-middle attacks

## Summary
Severity: High
Advisory: GHSA-27x4-j476-jp5f
CVE: CVE-2013-1633
CWE: CWE-319
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-27x4-j476-jp5f
Type: github-advisory

## Affected
- PyPI: `setuptools` — affected >=0 <0.7

## Details
easy_install in setuptools before 0.7 uses HTTP to retrieve packages from the PyPI repository, and does not perform integrity checks on package contents, which allows man-in-the-middle attackers to execute arbitrary code via a crafted response to the default use of the product.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1633
- https://github.com/pypa/advisory-database/tree/main/vulns/setuptools/PYSEC-2013-22.yaml
- https://github.com/pypa/setuptools
- https://pypi.python.org/pypi/setuptools/0.9.8#changes
- http://www.reddit.com/r/Python/comments/17rfh7/warning_dont_use_pip_in_an_untrusted_network_a
