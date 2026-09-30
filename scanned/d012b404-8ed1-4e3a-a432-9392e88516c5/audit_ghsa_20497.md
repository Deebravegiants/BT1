# [M] XML External Entity Reference in edu.stanford.nlp:stanford-corenlp

## Summary
Severity: Medium
Advisory: GHSA-mh83-jcw5-rjh8
CVE: CVE-2022-0198
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-01-14
Source: https://github.com/advisories/GHSA-mh83-jcw5-rjh8
Type: github-advisory

## Affected
- Maven: `edu.stanford.nlp:stanford-corenlp` — affected >=0

## Details
The TransformXML() function makes use of SAXParser generated from a SAXParserFactory with no FEATURE_SECURE_PROCESSING set, allowing for XXE attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0198
- https://github.com/stanfordnlp/corenlp/commit/1f52136321cfca68b991bd7870563d06cf96624d
- https://github.com/stanfordnlp/corenlp
- https://huntr.dev/bounties/3d7e70fe-dddd-4b79-af62-8e058c4d5763
