# [C] Access Control vulnerability within CoreNLP

## Summary
Severity: Critical
Advisory: GHSA-x2p8-rgfm-qw3v
CVE: CVE-2021-44550
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-25
Source: https://github.com/advisories/GHSA-x2p8-rgfm-qw3v
Type: github-advisory

## Affected
- Maven: `edu.stanford.nlp:stanford-corenlp` — affected >=0 <4.4.0

## Details
An Incorrect Access Control vulnerability exists in CoreNLP 4.3.2 via the classifier in NERServlet.java (lines 158 and 159).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44550
- https://github.com/stanfordnlp/CoreNLP/issues/1222
- https://github.com/stanfordnlp/CoreNLP/commit/5ee097dbede547023e88f60ed3f430ff09398b87
- https://github.com/stanfordnlp/CoreNLP
