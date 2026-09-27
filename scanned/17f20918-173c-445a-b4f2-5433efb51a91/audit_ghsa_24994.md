# [H] Cobbler subject to Command Injection

## Summary
Severity: High
Advisory: GHSA-g34c-mg6m-xvxj
CVE: CVE-2012-2395
CWE: CWE-77
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-g34c-mg6m-xvxj
Type: github-advisory

## Affected
- PyPI: `cobbler` — affected >=0 <2.6.0

## Details
A Command Injection in action_power.py in Cobbler prior to v2.6.0 allows remote attackers to execute arbitrary commands via shell metacharacters in the (1) username or (2) password fields to the power_system method in the xmlrpc API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2395
- https://github.com/cobbler/cobbler/issues/141
- https://github.com/cobbler/cobbler/commit/6d9167e5da44eca56bdf42b5776097a6779aaadf
- https://bugs.launchpad.net/ubuntu/+source/cobbler/+bug/978999
- https://github.com/cobbler/cobbler
- https://lists.opensuse.org/opensuse-security-announce/2012-05/msg00016.html
- https://lists.opensuse.org/opensuse-security-announce/2012-07/msg00000.html
- https://web.archive.org/web/20120712025653/http://www.securityfocus.com/bid/53666
- https://www.openwall.com/lists/oss-security/2012/05/23/18
- https://www.openwall.com/lists/oss-security/2012/05/23/4
- https://www.osvdb.org/82458
