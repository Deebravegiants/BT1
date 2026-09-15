# [H] Salt Improper Access Control

## Summary
Severity: High
Advisory: GHSA-vqh4-crjf-jjxx
CVE: CVE-2016-1866
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vqh4-crjf-jjxx
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=2015.8.0rc1 <2015.8.4

## Details
Salt 2015.8.x before 2015.8.4 does not properly handle clear messages on the minion, which allows man-in-the-middle attackers to execute arbitrary code by inserting packets into the minion-master data stream.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1866
- https://docs.saltstack.com/en/latest/topics/releases/2015.8.4.html
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2016-23.yaml
- https://github.com/saltstack/salt
- http://lists.opensuse.org/opensuse-updates/2016-03/msg00034.html
