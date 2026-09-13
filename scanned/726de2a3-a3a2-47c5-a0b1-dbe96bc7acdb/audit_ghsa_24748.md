# [H] Minion identity not validated in saltstack

## Summary
Severity: High
Advisory: GHSA-jmv9-5gx8-7xpf
CVE: CVE-2013-4439
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jmv9-5gx8-7xpf
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0.15.0 <0.17.1

## Details
Salt (aka SaltStack) before 0.15.0 through 0.17.0 allows remote authenticated minions to impersonate arbitrary minions via a crafted minion with a valid key.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4439
- https://github.com/saltstack/salt/pull/7356
- https://github.com/advisories/GHSA-jmv9-5gx8-7xpf
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2013-14.yaml
- https://github.com/saltstack/salt
- http://www.openwall.com/lists/oss-security/2013/10/18/3
