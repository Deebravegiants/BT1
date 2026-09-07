# [H] IPython vulnerable to cross site request forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-7fc2-rm35-2pp7
CVE: CVE-2015-5607
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7fc2-rm35-2pp7
Type: github-advisory

## Affected
- PyPI: `ipython` — affected >=0.12 <2.4.1
- PyPI: `ipython` — affected >=3.0.0 <3.2.3

## Details
IPython (Interactive Python) is a command shell. Cross-site request forgery in the REST API is possible in in IPython 2 and 3. Versions 2.4.1 and 3.2.3 contain patches.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5607
- https://github.com/ipython/ipython/commit/1415a9710407e7c14900531813c15ba6165f0816
- https://github.com/ipython/ipython/commit/a05fe052a18810e92d9be8c1185952c13fe4e5b0
- https://bugzilla.redhat.com/show_bug.cgi?id=1243842
- https://github.com/advisories/GHSA-7fc2-rm35-2pp7
- https://github.com/ipython/ipython
- https://github.com/pypa/advisory-database/tree/main/vulns/ipython/PYSEC-2017-47.yaml
- http://lists.fedoraproject.org/pipermail/package-announce/2015-July/162671.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-July/162936.html
- http://www.openwall.com/lists/oss-security/2015/07/21/3
