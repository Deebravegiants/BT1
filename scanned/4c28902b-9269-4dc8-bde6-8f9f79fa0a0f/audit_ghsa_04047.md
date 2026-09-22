# [C] Improper Authentication in Buildbot

## Summary
Severity: Critical
Advisory: GHSA-g86p-hgx5-2pfh
CVE: CVE-2019-12300
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-05-29
Source: https://github.com/advisories/GHSA-g86p-hgx5-2pfh
Type: github-advisory

## Affected
- PyPI: `buildbot` — affected >=0 <1.8.2
- PyPI: `buildbot` — affected >=2.0.0 <2.3.1

## Details
Buildbot before 1.8.2 and 2.x before 2.3.1 accepts a user-submitted authorization token from OAuth and uses it to authenticate a user. If an attacker has a token allowing them to read the user details of a victim, they can login as the victim.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12300
- https://github.com/advisories/GHSA-g86p-hgx5-2pfh
- https://github.com/buildbot/buildbot
- https://github.com/buildbot/buildbot/wiki/OAuth-vulnerability-in-using-submitted-authorization-token-for-authentication
- https://github.com/pypa/advisory-database/tree/main/vulns/buildbot/PYSEC-2019-6.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4XLOM2K4M4723BCLHZJEX52KJXZSEVRL
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7GXKO7OYLKBTXXXKF4VPHWT7GVYWFVYA
