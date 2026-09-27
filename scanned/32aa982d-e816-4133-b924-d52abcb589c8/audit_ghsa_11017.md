# [M] Apache PDFBox has Path Traversal through PDComplexFileSpecification.getFilename() function

## Summary
Severity: Medium
Advisory: GHSA-jjwr-xmw6-gf78
CVE: CVE-2026-23907
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-jjwr-xmw6-gf78
Type: github-advisory

## Affected
- Maven: `org.apache.pdfbox:pdfbox-examples` — affected >=2.0.24 <3.0.7

## Details
This issue affects the ExtractEmbeddedFiles example in Apache PDFBox: from 2.0.24 through 2.0.35, from 3.0.0 through 3.0.6.

The ExtractEmbeddedFiles example contains a path traversal vulnerability (CWE-22) because the filename that is obtained from PDComplexFileSpecification.getFilename() is appended to the extraction path.

Users who have copied this example into their production code should review it to ensure that the extraction path is acceptable. The example has been changed accordingly, now the initial path and the extraction paths are converted into canonical paths and it is verified that extraction path contains the initial path. The documentation has also been adjusted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-23907
- https://github.com/apache/pdfbox/commit/b028eafdf101b58e4ee95430c3be25e3e3aa29d7
- https://github.com/apache/pdfbox
- https://lists.apache.org/thread/gyfq5tcrxfv7rx0z2yyx4hb3h53ndffw
- http://www.openwall.com/lists/oss-security/2026/03/10/1
