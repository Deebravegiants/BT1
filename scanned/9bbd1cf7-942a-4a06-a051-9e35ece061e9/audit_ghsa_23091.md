# [H] pyshop vulnerable to man-in-the-middle attacks due to using HTTP to retrieve packages from the PyPI repository

## Summary
Severity: High
Advisory: GHSA-f594-f3v3-g649
CVE: CVE-2013-1630
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-f594-f3v3-g649
Type: github-advisory

## Affected
- PyPI: `pyshop` — affected >=0 <0.7.1

## Details
pyshop before 0.7.1 uses HTTP to retrieve packages from the PyPI repository, and does not perform integrity checks on package contents, which allows man-in-the-middle attackers to execute arbitrary code via a crafted response to a download operation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1630
- https://github.com/mardiros/pyshop/commit/ffadb0bcdef1e385884571670210cfd6ba351784
- https://github.com/mardiros/pyshop
- https://github.com/mardiros/pyshop/blob/master/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/pyshop/PYSEC-2013-10.yaml
- http://www.reddit.com/r/Python/comments/17rfh7/warning_dont_use_pip_in_an_untrusted_network_a
