# [M] Apache PDFBox Examples: Path Traversal in PDFBox ExtractEmbeddedFiles Example Code

## Summary
Severity: Medium
Advisory: GHSA-gcj8-76p4-g2fq
CVE: CVE-2026-33929
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-gcj8-76p4-g2fq
Type: github-advisory

## Affected
- Maven: `org.apache.pdfbox:pdfbox-examples` — affected >=2.0.24 <2.0.37
- Maven: `org.apache.pdfbox:pdfbox-examples` — affected >=3.0.0 <3.0.8

## Details
Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') vulnerability in Apache PDFBox Examples.

This issue affects the 
ExtractEmbeddedFiles example in Apache PDFBox: from 2.0.24 through 2.0.36, from 3.0.0 through 3.0.7.


Users are recommended to update to version 2.0.37 or 3.0.8 once available. Until then, they should apply the fix provided in GitHub PR 427.

The ExtractEmbeddedFiles example contained a path traversal vulnerability (CWE-22) mentioned in CVE-2026-23907. However the change in the releases 2.0.36 and 3.0.7 is flawed because it doesn't consider the file path separator. Because of that, a user having writing rights on /home/ABC could be victim to a malicious PDF resulting in a write attempt to any path starting with /home/ABC, e.g. "/home/ABCDEF".

Users who have copied this example into their production code should apply the mentioned change. The example 
has been changed accordingly and is available in the project repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33929
- https://github.com/apache/pdfbox/pull/427/changes
- https://github.com/apache/pdfbox
- https://lists.apache.org/thread/j8l07tgzy9dm8d8n0f3c45h7zg7t3ld6
- https://lists.apache.org/thread/op3lyx1ngzy4qycn06l6hljyf28ff0zs
