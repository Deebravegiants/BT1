# [H] NLTK has a Path Traversal issue

## Summary
Severity: High
Advisory: GHSA-68j8-pq59-fqgm
CVE: CVE-2026-0847
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-68j8-pq59-fqgm
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0

## Details
A vulnerability in NLTK versions up to and including 3.9.2 allows arbitrary file read via path traversal in multiple CorpusReader classes, including WordListCorpusReader, TaggedCorpusReader, and BracketParseCorpusReader. These classes fail to properly sanitize or validate file paths, enabling attackers to traverse directories and access sensitive files on the server. This issue is particularly critical in scenarios where user-controlled file inputs are processed, such as in machine learning APIs, chatbots, or NLP pipelines. Exploitation of this vulnerability can lead to unauthorized access to sensitive files, including system files, SSH private keys, and API tokens, and may potentially escalate to remote code execution when combined with other vulnerabilities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0847
- https://github.com/nltk/nltk
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2026-98.yaml
- https://huntr.com/bounties/fc69914f-36a9-4c18-8503-10013b39f966
