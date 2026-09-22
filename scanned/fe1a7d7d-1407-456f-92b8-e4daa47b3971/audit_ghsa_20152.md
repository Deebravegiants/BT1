# [M] Denial of Service in python-ldap

## Summary
Severity: Medium
Advisory: GHSA-qfr5-wjpw-q4c4
CVE: CVE-2021-46823
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-19
Source: https://github.com/advisories/GHSA-qfr5-wjpw-q4c4
Type: github-advisory

## Affected
- PyPI: `python-ldap` — affected >=0 <3.4.0

## Details
python-ldap before 3.4.0 is vulnerable to a denial of service when ldap.schema is used for untrusted schema definitions, because of a regular expression denial of service (ReDoS) flaw in the LDAP schema parser. By sending crafted regex input, a remote authenticated attacker could exploit this vulnerability to cause a denial of service condition.

## References
- https://github.com/python-ldap/python-ldap/security/advisories/GHSA-r8wq-qrxc-hmcm
- https://nvd.nist.gov/vuln/detail/CVE-2021-46823
- https://exchange.xforce.ibmcloud.com/vulnerabilities/221507
- https://github.com/python-ldap/python-ldap
