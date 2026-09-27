# [H] Slixmpp lacks SSL Certificate hostname validation in XMLStream

## Summary
Severity: High
Advisory: GHSA-q6cq-m9gm-6q2f
CVE: CVE-2022-45197
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-12-25
Source: https://github.com/advisories/GHSA-q6cq-m9gm-6q2f
Type: github-advisory

## Affected
- PyPI: `slixmpp` — affected >=0 <1.8.3

## Details
Slixmpp before 1.8.3 lacks SSL Certificate hostname validation in XMLStream, allowing an attacker to pose as any server in the eyes of Slixmpp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45197
- https://github.com/poezio/slixmpp
- https://github.com/poezio/slixmpp/commits/master/slixmpp/xmlstream/xmlstream.py
- https://github.com/poezio/slixmpp/tags
- https://github.com/pypa/advisory-database/tree/main/vulns/slixmpp/PYSEC-2022-43013.yaml
- https://lab.louiz.org/poezio/slixmpp/-/commit/b60b1b985db928532f97c4f61d6fbc801f0aa7fa
- https://lab.louiz.org/poezio/slixmpp/-/commits/master
- https://security.gentoo.org/glsa/202305-07
