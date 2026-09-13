# [H] pyrad is vulnerable to the use of Insufficiently Random Values

## Summary
Severity: High
Advisory: GHSA-q4v3-wmm6-hcrx
CVE: CVE-2013-0294
CWE: CWE-330
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-q4v3-wmm6-hcrx
Type: github-advisory

## Affected
- PyPI: `pyrad` — affected >=0 <2.1

## Details
packet.py in pyrad before 2.1 uses weak random numbers to generate RADIUS authenticators and hash passwords, which makes it easier for remote attackers to obtain sensitive information via a brute force attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0294
- https://github.com/wichert/pyrad/commit/38f74b36814ca5b1a27d9898141126af4953bee5
- https://bugzilla.redhat.com/show_bug.cgi?id=911682
- https://exchange.xforce.ibmcloud.com/vulnerabilities/82133
- https://github.com/pypa/advisory-database/tree/main/vulns/pyrad/PYSEC-2020-211.yaml
- https://github.com/pyradius/pyrad
- https://web.archive.org/web/20200228160027/http://www.securityfocus.com/bid/57984
- http://lists.fedoraproject.org/pipermail/package-announce/2013-September/115677.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-September/115705.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-September/116567.html
- http://www.openwall.com/lists/oss-security/2013/02/15/13
