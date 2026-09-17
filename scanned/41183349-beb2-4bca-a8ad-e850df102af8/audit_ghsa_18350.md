# [H] MinIO Java Client XML Tag Value Substitution Vulnerability

## Summary
Severity: High
Advisory: GHSA-h7rh-xfpj-hpcm
CVE: CVE-2025-59952
CWE: CWE-20, CWE-91
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-29
Source: https://github.com/advisories/GHSA-h7rh-xfpj-hpcm
Type: github-advisory

## Affected
- Maven: `io.minio:minio` — affected >=0 <8.6.0

## Details
#### Description
In minio-java versions prior to 8.6.0, XML tag values containing references to system properties or environment variables were automatically substituted with their actual values during processing. This unintended behavior could lead to the exposure of sensitive information, including credentials, file paths, or system configuration details, if such references were present in XML content from untrusted sources.

#### Affected Versions
- minio-java < 8.6.0

All applications utilizing affected versions of minio-java for parsing XML with potentially untrusted input are vulnerable.

#### Impact
This vulnerability poses a high risk of information disclosure. Attackers could craft malicious XML inputs to extract sensitive data from the system's properties or environment variables, potentially compromising security in applications relying on minio-java for object storage operations.

#### Patches
The issue is resolved in minio-java version 8.6.0 and later. In these versions, automatic substitution of XML tag values with system properties or environment variables has been disabled.

Users are strongly advised to upgrade to minio-java 8.6.0 or a newer release to mitigate the vulnerability.

#### Workarounds
No full workarounds exist without upgrading the library. As interim measures:

- Refrain from processing XML data from untrusted or external sources.
- Implement input sanitization or validation to detect and remove references to 
  system properties or environment variables in XML content.

## References
- https://github.com/minio/minio-java/security/advisories/GHSA-h7rh-xfpj-hpcm
- https://nvd.nist.gov/vuln/detail/CVE-2025-59952
- https://github.com/minio/minio-java/commit/f7a98d06b25e5464bdd4811b044e25ff9101d37f
- https://github.com/minio/minio-java
- https://github.com/minio/minio-java/releases/tag/8.6.0
