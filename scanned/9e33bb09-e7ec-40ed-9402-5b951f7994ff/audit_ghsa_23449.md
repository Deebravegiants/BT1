# [H] SaltStack Salt Authentication Bypass when using the local_batch client from salt-api

## Summary
Severity: High
Advisory: GHSA-f2h7-4f84-8qrm
CVE: CVE-2017-5192
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-f2h7-4f84-8qrm
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <2015.8.13
- PyPI: `salt` — affected >=2016.3.0 <2016.3.5
- PyPI: `salt` — affected >=2016.11.0 <2016.11.2

## Details
When using the local_batch client from salt-api in SaltStack Salt before 2015.8.13, 2016.3.x before 2016.3.5, and 2016.11.x before 2016.11.2, external authentication is not respected, enabling all authentication to be bypassed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5192
- https://docs.saltstack.com/en/2016.3/topics/releases/2015.8.13.html
- https://docs.saltstack.com/en/2016.3/topics/releases/2016.3.5.html
- https://docs.saltstack.com/en/latest/topics/releases/2016.11.2.html
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2017-38.yaml
- https://github.com/saltstack/salt
