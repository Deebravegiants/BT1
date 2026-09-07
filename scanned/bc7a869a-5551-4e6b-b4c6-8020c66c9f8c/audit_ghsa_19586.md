# [M] Apache POI OOXML Vulnerable to Improper Input Validation in OOXML File Parsing

## Summary
Severity: Medium
Advisory: GHSA-gmg8-593g-7mv3
CVE: CVE-2025-31672
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-04-09
Source: https://github.com/advisories/GHSA-gmg8-593g-7mv3
Type: github-advisory

## Affected
- Maven: `org.apache.poi:poi-ooxml` — affected >=0 <5.4.0

## Details
Improper Input Validation vulnerability in Apache POI. The issue affects the parsing of OOXML format files like xlsx, docx and pptx. These file formats are basically zip files and it is possible for malicious users to add zip entries with duplicate names (including the path) in the zip. In this case, products reading the affected file could read different data because 1 of the zip entries with the duplicate name is selected over another but different products may choose a different zip entry.
This issue affects Apache POI poi-ooxml before 5.4.0. poi-ooxml 5.4.0 has a check that throws an exception if zip entries with duplicate file names are found in the input file.
Users are recommended to upgrade to version poi-ooxml 5.4.0, which fixes the issue. Please read  https://poi.apache.org/security.html  for recommendations about how to use the POI libraries securely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-31672
- https://bz.apache.org/bugzilla/show_bug.cgi?id=69620
- https://github.com/apache/poi
- https://lists.apache.org/thread/k14w8vcjqy4h34hh5kzldko78kpylkq5
- https://security.netapp.com/advisory/ntap-20250523-0004
- http://www.openwall.com/lists/oss-security/2025/04/08/2
