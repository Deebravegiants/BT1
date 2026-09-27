# [H] Trac is vulnerable to improper policy checks and missing 'raw' role check in docutils

## Summary
Severity: High
Advisory: GHSA-f9qv-j5g6-g5cr
CVE: CVE-2009-4405
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-f9qv-j5g6-g5cr
Type: github-advisory

## Affected
- PyPI: `trac` — affected >=0 <0.11.6

## Details
Multiple unspecified vulnerabilities in Trac before 0.11.6 have unknown impact and attack vectors, possibly related to (1) "policy checks in report results when using alternate formats" or (2) a "check for the 'raw' role that is missing in docutils < 0.6."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-4405
- https://bugzilla.redhat.com/show_bug.cgi?id=542394
- https://exchange.xforce.ibmcloud.com/vulnerabilities/54983
- https://github.com/pypa/advisory-database/tree/main/vulns/trac/PYSEC-2009-7.yaml
- https://web.archive.org/web/20130417170303/http://secunia.com/advisories/37901
- https://web.archive.org/web/20130513235205/http://secunia.com/advisories/37807
- https://www.redhat.com/archives/fedora-package-announce/2009-December/msg01169.html
- http://trac.edgewall.org/browser/tags/trac-0.11.6/RELEASE
