# [M] Salt Insecure configuration of PAM external authentication service

## Summary
Severity: Medium
Advisory: GHSA-v2rp-9cpj-pfw2
CVE: CVE-2016-3176
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v2rp-9cpj-pfw2
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <2015.5.10
- PyPI: `salt` — affected >=2015.8 <2015.8.8

## Details
Salt before 2015.5.10 and 2015.8.x before 2015.8.8, when PAM external authentication is enabled, allows attackers to bypass the configured authentication service by passing an alternate service with a command sent to LocalClient.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3176
- https://docs.saltstack.com/en/latest/topics/releases/2015.5.10.html
- https://docs.saltstack.com/en/latest/topics/releases/2015.8.8.html
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2017-33.yaml
- https://github.com/saltstack/salt
