# [H] SaltStack Privilege Escalation vulnerability

## Summary
Severity: High
Advisory: GHSA-7wx3-vr2f-6p29
CVE: CVE-2013-6617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7wx3-vr2f-6p29
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0.11.0 <0.17.1

## Details
The salt master in Salt (aka SaltStack) 0.11.0 through 0.17.0 does not properly drop group privileges, which makes it easier for remote attackers to gain privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-6617
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2013-15.yaml
- https://github.com/saltstack/salt
- http://docs.saltstack.com/topics/releases/0.17.1.html
