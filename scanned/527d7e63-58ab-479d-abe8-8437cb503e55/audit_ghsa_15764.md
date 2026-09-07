# [M] Apache StreamPipes potentially allows creation of multiple identical accounts

## Summary
Severity: Medium
Advisory: GHSA-2qph-v9p2-q2gv
CVE: CVE-2024-30471
CWE: CWE-367
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-2qph-v9p2-q2gv
Type: github-advisory

## Affected
- Maven: `org.apache.streampipes:streampipes-parent` — affected >=0 <0.95.0
- PyPI: `streampipes` — affected >=0 <0.95.0

## Details
Time-of-check Time-of-use (TOCTOU) Race Condition vulnerability in Apache StreamPipes in user self-registration.
This allows an attacker to potentially request the creation of multiple accounts with the same email address until the email address is registered, creating many identical users and corrupting StreamPipe's user management.
This issue affects Apache StreamPipes: through 0.93.0.

Users are recommended to upgrade to version 0.95.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-30471
- https://github.com/apache/streampipes
- https://github.com/apache/streampipes/releases/tag/release%2F0.95.0
- https://github.com/pypa/advisory-database/tree/main/vulns/streampipes/PYSEC-2024-172.yaml
- https://lists.apache.org/thread/8yodrmohgcybq900or3d4hc1msl230fr
- http://www.openwall.com/lists/oss-security/2024/07/16/9
