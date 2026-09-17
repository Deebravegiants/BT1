# [H] Apache Xerces C++: Use-after-free on external DTD scan

## Summary
Severity: High
Advisory: CVE-2024-23807
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2024-23807
Type: osv

## Details
The Apache Xerces C++ XML parser on versions 3.0.0 before 3.2.5 contains a use-after-free error triggered during the scanning of external DTDs.

Users are recommended to upgrade to version 3.2.5 which fixes the issue, or mitigate the issue by disabling DTD processing. This can be accomplished via the DOM using a standard parser feature, or via SAX using the XERCES_DISABLE_DTD environment variable.

This issue has been disclosed before as CVE-2018-1311, but unfortunately that advisory incorrectly stated the issue would be fixed in version 3.2.3 or 3.2.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23807.json
- https://lists.apache.org/thread/c497tgn864tsbm8w0bo3f0d81s07zk9r
- https://nvd.nist.gov/vuln/detail/CVE-2024-23807
- https://github.com/apache/xerces-c/pull/54
