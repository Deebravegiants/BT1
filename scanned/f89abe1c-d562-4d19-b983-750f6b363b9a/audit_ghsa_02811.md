# [H] Improper Restriction of Excessive Authentication Attempts in py-bcrypt

## Summary
Severity: High
Advisory: GHSA-r838-q6jp-58xx
CVE: CVE-2013-1895
CWE: CWE-307
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-r838-q6jp-58xx
Type: github-advisory

## Affected
- PyPI: `py-bcrypt` — affected >=0 <0.3

## Details
The py-bcrypt module before 0.3 for Python does not properly handle concurrent memory access, which allows attackers to bypass authentication via multiple authentication requests, which trigger the password hash to be overwritten.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1895
- https://exchange.xforce.ibmcloud.com/vulnerabilities/83039
- https://github.com/advisories/GHSA-r838-q6jp-58xx
- https://github.com/grnet/python-bcrypt
- https://github.com/pypa/advisory-database/tree/main/vulns/py-bcrypt/PYSEC-2020-249.yaml
- http://lists.fedoraproject.org/pipermail/package-announce/2013-April/101382.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-April/101387.html
- http://www.openwall.com/lists/oss-security/2013/03/26/2
