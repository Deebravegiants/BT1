# [M] Trac Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rcmj-xp8f-f6q4
CVE: CVE-2008-2951
CWE: CWE-20, CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-rcmj-xp8f-f6q4
Type: github-advisory

## Affected
- PyPI: `trac` — affected >=0 <0.10.5

## Details
Open redirect vulnerability in the search script in Trac before 0.10.5 allows remote attackers to redirect users to arbitrary web sites and conduct phishing attacks via a URL in the q parameter, possibly related to the quickjump function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-2951
- https://exchange.xforce.ibmcloud.com/vulnerabilities/44043
- https://github.com/pypa/advisory-database/tree/main/vulns/trac/PYSEC-2008-4.yaml
- https://www.redhat.com/archives/fedora-package-announce/2008-July/msg01261.html
- https://www.redhat.com/archives/fedora-package-announce/2008-July/msg01270.html
- http://holisticinfosec.org/content/view/72/45
- http://trac.edgewall.org/wiki/ChangeLog
