# [C] Code injection in stanford-parser

## Summary
Severity: Critical
Advisory: GHSA-353m-jh2m-72v4
CVE: CVE-2023-39020
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-28
Source: https://github.com/advisories/GHSA-353m-jh2m-72v4
Type: github-advisory

## Affected
- Maven: `edu.stanford.nlp:stanford-parser` — affected >=0 <4.5.5

## Details
stanford-parser v3.9.2 and below was discovered to contain a code injection vulnerability in the component edu.stanford.nlp.io.getBZip2PipedInputStream. This vulnerability is exploited via passing an unchecked argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39020
- https://github.com/stanfordnlp/CoreNLP/commit/897231bed0efb24574c80c875c0b5f2225c145bc
- https://github.com/LetianYuan/My-CVE-Public-References/tree/main/edu_stanford_nlp_stanford-parser
- https://github.com/stanfordnlp/CoreNLP
