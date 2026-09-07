# [C] Improper Certificate Validation in Twisted

## Summary
Severity: Critical
Advisory: GHSA-65rm-h285-5cc5
CVE: CVE-2019-12855
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2019-08-16
Source: https://github.com/advisories/GHSA-65rm-h285-5cc5
Type: github-advisory

## Affected
- PyPI: `Twisted` — affected >=0 <19.7.0rc1

## Details
In words.protocols.jabber.xmlstream in Twisted through 19.2.1, XMPP support did not verify certificates when used with TLS, allowing an attacker to MITM connections.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12855
- https://github.com/twisted/twisted/pull/1147
- https://github.com/pypa/advisory-database/tree/main/vulns/twisted/PYSEC-2019-129.yaml
- https://github.com/twisted/twisted
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PLTZDMFBNFSJMBXYJNGJHENJA4H2TSMZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PLTZDMFBNFSJMBXYJNGJHENJA4H2TSMZ
- https://twistedmatrix.com/trac/ticket/9561
- https://usn.ubuntu.com/4308-1
- https://usn.ubuntu.com/4308-2
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00013.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00028.html
