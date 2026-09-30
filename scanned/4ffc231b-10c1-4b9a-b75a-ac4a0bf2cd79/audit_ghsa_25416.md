# [C] SaltStack Salt is vulnerable to command injection

## Summary
Severity: Critical
Advisory: GHSA-q53j-p6r2-g2v4
CVE: CVE-2019-17361
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q53j-p6r2-g2v4
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <2019.2.3

## Details
In SaltStack Salt before 2019.2.3, the salt-api NET API with the ssh client enabled is vulnerable to command injection. This allows an unauthenticated attacker with network access to the API endpoint to execute arbitrary code on the salt-api host.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17361
- https://docs.saltstack.com/en/latest/topics/releases/2019.2.3.html#security-fix
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2020-177.yaml
- https://github.com/saltstack/salt
- https://usn.ubuntu.com/4459-1
- https://www.debian.org/security/2020/dsa-4676
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00026.html
