# [C] Cobbler has Exposed Dangerous Method or Function

## Summary
Severity: Critical
Advisory: GHSA-8787-63px-3m23
CVE: CVE-2018-10931
CWE: CWE-749
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8787-63px-3m23
Type: github-advisory

## Affected
- PyPI: `cobbler` — affected >=2.6.0 <3.0.0

## Details
It was found that cobbler 2.6.x exposed all functions from its CobblerXMLRPCInterface class over XMLRPC. A remote, unauthenticated attacker could use this flaw to gain high privileges within cobbler, upload files to arbitrary location in the context of the daemon.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10931
- https://github.com/cobbler/cobbler/issues/1916
- https://github.com/cobbler/cobbler/pull/1921
- https://github.com/cobbler/cobbler/commit/1b91a3d3ac87c31d9dac2307513feb2aa49620a6
- https://access.redhat.com/errata/RHSA-2018:2372
- https://access.redhat.com/security/cve/CVE-2018-10931
- https://bugzilla.redhat.com/show_bug.cgi?id=1613861
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10931
- https://github.com/cobbler/cobbler
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5P5Q4ACIVZ5D4KSUDLGRTOKGGB4U42SD
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CMWK5KCCZXOGOYNR2H6BWDSABTQ5NYJA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5P5Q4ACIVZ5D4KSUDLGRTOKGGB4U42SD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CMWK5KCCZXOGOYNR2H6BWDSABTQ5NYJA
- https://movermeyer.com/2018-08-02-privilege-escalation-exploits-in-cobblers-api
