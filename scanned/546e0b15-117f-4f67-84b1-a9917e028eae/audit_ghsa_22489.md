# [H] SaltStack Salt Information Exposure

## Summary
Severity: High
Advisory: GHSA-xcx4-5wq7-g5g7
CVE: CVE-2017-8109
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-xcx4-5wq7-g5g7
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=2016.11 <2016.11.4

## Details
The salt-ssh minion code in SaltStack Salt 2016.11 before 2016.11.4 copied over configuration from the Salt Master without adjusting permissions, which might leak credentials to local attackers on configured minions (clients).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8109
- https://github.com/saltstack/salt/issues/40075
- https://github.com/saltstack/salt/pull/40609
- https://github.com/saltstack/salt/pull/40609/commits/6e34c2b5e5e849302af7ccd00509929c3809c658
- https://bugzilla.suse.com/show_bug.cgi?id=1035912
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2017-82.yaml
- https://github.com/saltstack/salt
