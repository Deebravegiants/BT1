# [H] Apache StreamPipes has potential remote code execution (RCE) via file upload

## Summary
Severity: High
Advisory: GHSA-6523-jf4r-c962
CVE: CVE-2024-31411
CWE: CWE-434
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-6523-jf4r-c962
Type: github-advisory

## Affected
- Maven: `org.apache.streampipes:streampipes-parent` — affected >=0 <0.95.0
- PyPI: `streampipes` — affected >=0 <0.95.0

## Details
Unrestricted Upload of File with dangerous type vulnerability in Apache StreamPipes.
Such a dangerous type might be an executable file that may lead to a remote code execution (RCE).
The unrestricted upload is only possible for authenticated and authorized users.

This issue affects Apache StreamPipes: through 0.93.0.

Users are recommended to upgrade to version 0.95.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31411
- https://github.com/apache/streampipes
- https://github.com/apache/streampipes/releases/tag/release%2F0.95.0
- https://github.com/pypa/advisory-database/tree/main/vulns/streampipes/PYSEC-2024-173.yaml
- https://lists.apache.org/thread/b0657okbwzg5xxs11hphvc9qrd9s70mt
- http://www.openwall.com/lists/oss-security/2024/07/16/10
