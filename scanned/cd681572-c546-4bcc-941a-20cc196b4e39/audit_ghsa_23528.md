# [M] Python RSA allows attackers to spoof signatures

## Summary
Severity: Medium
Advisory: GHSA-8rjr-6qq5-pj9p
CVE: CVE-2016-1494
CWE: CWE-20, CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-8rjr-6qq5-pj9p
Type: github-advisory

## Affected
- PyPI: `rsa` — affected >=0 <3.3

## Details
The verify function in the RSA package for Python (Python-RSA) before 3.3 allows attackers to spoof signatures with a small public exponent via crafted signature padding, aka a BERserk attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1494
- https://github.com/sybrenstuvel/python-rsa/commit/ab5d21c3b554f926d51ff3ad9c794bcf32e95b3c
- https://bitbucket.org/sybren/python-rsa/pull-requests/14/security-fix-bb06-attack-in-verify-by/diff
- https://blog.filippo.io/bleichenbacher-06-signature-forgery-in-python-rsa
- https://github.com/pypa/advisory-database/tree/main/vulns/rsa/PYSEC-2016-10.yaml
- https://github.com/sybrenstuvel/python-rsa
- https://web.archive.org/web/20210123020914/http://www.securityfocus.com/bid/79829
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175897.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175942.html
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00032.html
- http://www.openwall.com/lists/oss-security/2016/01/05/1
- http://www.openwall.com/lists/oss-security/2016/01/05/3
