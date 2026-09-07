# [M] Libextractor multiple heap-based buffer overflows

## Summary
Severity: Medium
Advisory: GHSA-f836-7jqw-3684
CVE: CVE-2006-2458
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-f836-7jqw-3684
Type: github-advisory

## Affected
- PyPI: `extractor` — affected 0.5

## Details
Multiple heap-based buffer overflows in Libextractor 0.5.13 and earlier allow remote attackers to execute arbitrary code via (1) the asf_read_header function in the ASF plugin (plugins/asfextractor.c), and (2) the parse_trak_atom function in the QT plugin (plugins/qtextractor.c).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-2458
- https://exchange.xforce.ibmcloud.com/vulnerabilities/26531
- https://exchange.xforce.ibmcloud.com/vulnerabilities/26532
- https://github.com/pypa/advisory-database/tree/main/vulns/extractor/PYSEC-2006-4.yaml
- http://gnunet.org/libextractor
- http://www.debian.org/security/2006/dsa-1081
- http://www.gentoo.org/security/en/glsa/glsa-200605-14.xml
