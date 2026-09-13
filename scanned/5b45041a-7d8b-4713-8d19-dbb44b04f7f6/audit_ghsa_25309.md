# [H] Zope Denial of Service (DoS) vulnerability in ZServer

## Summary
Severity: High
Advisory: GHSA-qh4q-fwf8-qqrw
CVE: CVE-2010-3198
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qh4q-fwf8-qqrw
Type: github-advisory

## Affected
- PyPI: `Zope` — affected >=2.10.0 <2.10.12
- PyPI: `Zope` — affected >=2.11.0 <2.11.7

## Details
ZServer in Zope 2.10.x before 2.10.12 and 2.11.x before 2.11.7 allows remote attackers to cause a denial of service (crash of worker threads) via vectors that trigger uncaught exceptions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-3198
- https://github.com/zopefoundation/Zope/commit/0f2f56f63e4a4d695ee670e02b317e900550dbac
- https://github.com/zopefoundation/Zope/commit/e03a5f036d42ed2426886c9035fe018eeec65de4
- https://bugs.launchpad.net/zope2/+bug/627988
- https://github.com/pypa/advisory-database/tree/main/vulns/zope/PYSEC-2010-32.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/zope/PYSEC-2010-33.yaml
- https://github.com/zopefoundation/Zope
- https://mail.zope.org/pipermail/zope-announce/2010-September/002247.html
- https://web.archive.org/web/20200229173503/http://www.securityfocus.com/bid/42939
- http://www.zope.org/Products/Zope/2.10.12/CHANGES.txt
- http://www.zope.org/Products/Zope/2.11.7/CHANGES.txt
