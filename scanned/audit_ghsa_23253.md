# [H] python-bugzilla has improper validation of X.509 certificates

## Summary
Severity: High
Advisory: GHSA-2q4h-27m7-rj67
CVE: CVE-2013-2191
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-2q4h-27m7-rj67
Type: github-advisory

## Affected
- PyPI: `python-bugzilla` — affected >=0 <0.9.0

## Details
python-bugzilla before 0.9.0 does not validate X.509 certificates, which allows man-in-the-middle attackers to spoof Bugzilla servers via a crafted certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2191
- https://github.com/python-bugzilla/python-bugzilla/commit/a782282ee479ba4cc1b8b1d89700ac630ba83eef
- https://bugzilla.redhat.com/show_bug.cgi?id=951594
- https://git.fedorahosted.org/cgit/python-bugzilla.git/commit/?id=a782282ee479ba4cc1b8b1d89700ac630ba83eef
- https://github.com/pypa/advisory-database/tree/main/vulns/python-bugzilla/PYSEC-2014-88.yaml
- https://github.com/python-bugzilla/python-bugzilla
- https://lists.fedorahosted.org/pipermail/python-bugzilla/2013-June/000104.html
- http://lists.opensuse.org/opensuse-updates/2013-07/msg00025.html
- http://lists.opensuse.org/opensuse-updates/2013-07/msg00026.html
- http://www.openwall.com/lists/oss-security/2013/06/19/6
