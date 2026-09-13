# [H] Apache James vulnerable to denial of service through the use of IMAP literals

## Summary
Severity: High
Advisory: GHSA-56jp-w6vw-j3jw
CVE: CVE-2024-37358
CWE: CWE-20, CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-56jp-w6vw-j3jw
Type: github-advisory

## Affected
- Maven: `org.apache.james.protocols:protocols-imap` — affected >=0 <3.7.6
- Maven: `org.apache.james.protocols:protocols-imap` — affected >=3.8.0 <3.8.2

## Details
Similarly to CVE-2024-34055, Apache James is vulnerable to denial of service through the abuse of IMAP literals from both authenticated and unauthenticated users, which could be used to cause unbounded memory allocation and very long computations

Version 3.7.6 and 3.8.2 restrict such illegitimate use of IMAP literals.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37358
- https://github.com/apache/james-project/commit/6dd3ad9ea1f6a9bc887d2c7af3f5aa30a60ec769
- https://github.com/apache/james-project/commit/b2f3c06edfd37b409121bf04c56a6f026048a77e
- https://github.com/apache/james-project
- https://lists.apache.org/thread/1pxsh11v5s3fkvhnqvkmlqwt3fgpcrqc
