# [H] Improper Authentication in pip

## Summary
Severity: High
Advisory: GHSA-c5h8-cq4v-cvfm
CVE: CVE-2013-5123
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c5h8-cq4v-cvfm
Type: github-advisory

## Affected
- PyPI: `pip` — affected >=0 <1.5

## Details
The mirroring support (-M, --use-mirrors) in Python Pip before 1.5 uses insecure DNS querying and authenticity checks which allows attackers to perform man-in-the-middle attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-5123
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2013-5123
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2013-5123
- https://github.com/advisories/GHSA-c5h8-cq4v-cvfm
- https://github.com/pypa/advisory-database/tree/main/vulns/pip/PYSEC-2019-160.yaml
- https://security-tracker.debian.org/tracker/CVE-2013-5123
- http://lists.fedoraproject.org/pipermail/package-announce/2015-April/155248.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-April/155291.html
- http://www.openwall.com/lists/oss-security/2013/08/21/17
- http://www.openwall.com/lists/oss-security/2013/08/21/18
