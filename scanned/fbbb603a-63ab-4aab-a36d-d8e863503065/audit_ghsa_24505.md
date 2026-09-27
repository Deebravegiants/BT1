# [H] SaltStack Salt arbitrary command execution in Salt-api via ssh_client

## Summary
Severity: High
Advisory: GHSA-8r7r-x48r-pf8f
CVE: CVE-2017-5200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8r7r-x48r-pf8f
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <2015.8.13
- PyPI: `salt` — affected >=2016.3.0 <2016.3.5
- PyPI: `salt` — affected >=2016.11.0 <2016.11.2

## Details
Salt-api in SaltStack Salt before 2015.8.13, 2016.3.x before 2016.3.5, and 2016.11.x before 2016.11.2 allows arbitrary command execution on a salt-master via Salt's ssh_client.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5200
- https://docs.saltstack.com/en/2016.3/topics/releases/2015.8.13.html
- https://docs.saltstack.com/en/2016.3/topics/releases/2016.3.5.html
- https://docs.saltstack.com/en/latest/topics/releases/2016.11.2.html
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2017-39.yaml
- https://github.com/saltstack/salt
