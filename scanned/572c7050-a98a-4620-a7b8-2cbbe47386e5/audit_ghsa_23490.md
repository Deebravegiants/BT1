# [M] Zope allows remote attackers to read arbitrary files

## Summary
Severity: Medium
Advisory: GHSA-hm8g-jxjj-gfm3
CVE: CVE-2006-4684
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-hm8g-jxjj-gfm3
Type: github-advisory

## Affected
- PyPI: `zope2` — affected >=2.7.0
- PyPI: `zope2` — affected >=2.8.0 <2.8.9

## Details
The docutils module in Zope (Zope2) 2.7.0 through 2.7.9 and 2.8.0 through 2.8.8 does not properly handle web pages with reStructuredText (reST) markup, which allows remote attackers to read arbitrary files via a csv_table directive, a different vulnerability than CVE-2006-3458.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-4684
- https://github.com/pypa/advisory-database/tree/main/vulns/zope2/PYSEC-2006-8.yaml
- https://github.com/zopefoundation/Zope
- http://mail.zope.org/pipermail/zope-announce/2006-August/002005.html
- http://www.debian.org/security/2006/dsa-1176
- http://www.zope.org/Products/Zope/Hotfix-2006-08-21/Hotfix-20060821/README.txt
