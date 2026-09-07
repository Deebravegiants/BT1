# [H] Python-saml allows manipulation of SAML data without invalidation of cryptographic signature

## Summary
Severity: High
Advisory: GHSA-j8j8-348v-wfm3
CVE: CVE-2017-11427
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2019-07-05
Source: https://github.com/advisories/GHSA-j8j8-348v-wfm3
Type: github-advisory

## Affected
- PyPI: `python-saml` — affected >=0 <2.4.0

## Details
OneLogin PythonSAML 2.3.0 and earlier may incorrectly utilize the results of XML DOM traversal and canonicalization APIs in such a way that an attacker may be able to manipulate the SAML data without invalidating the cryptographic signature, allowing the attack to potentially bypass authentication to SAML service providers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11427
- https://github.com/SAML-Toolkits/python-saml/commit/fad881b4432febea69d70691dfed51c93f0de10f
- https://duo.com/blog/duo-finds-saml-vulnerabilities-affecting-multiple-implementations
- https://github.com/SAML-Toolkits/python-saml
- https://github.com/advisories/GHSA-j8j8-348v-wfm3
- https://github.com/pypa/advisory-database/tree/main/vulns/python-saml/PYSEC-2019-198.yaml
- https://www.kb.cert.org/vuls/id/475445
