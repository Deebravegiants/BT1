# [H] Salt has insufficient argument validation in several modules

## Summary
Severity: High
Advisory: GHSA-v89f-4mc4-h6w9
CVE: CVE-2013-4435
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v89f-4mc4-h6w9
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0.15.0 <0.17.1

## Details
Salt (aka SaltStack) 0.15.0 through 0.17.0 allows remote authenticated users who are using external authentication or client ACL to execute restricted routines by embedding the routine in another routine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4435
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2013-12.yaml
- https://github.com/saltstack/salt
- https://github.com/saltstack/salt/blob/master/doc/topics/releases/0.17.1.rst
- http://docs.saltstack.com/topics/releases/0.17.1.html
- http://www.openwall.com/lists/oss-security/2013/10/18/3
