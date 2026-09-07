# [C] Apache StreamPipes: Use of Cryptographically Weak Pseudo-Random Number Generator (PRNG) in Recovery Token Generation

## Summary
Severity: Critical
Advisory: GHSA-cf3q-vg8w-mw84
CVE: CVE-2024-29868
CWE: CWE-338
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-06-24
Source: https://github.com/advisories/GHSA-cf3q-vg8w-mw84
Type: github-advisory

## Affected
- Maven: `org.apache.streampipes:streampipes-resource-management` — affected >=0.69.0 <0.95.0

## Details
Use of Cryptographically Weak Pseudo-Random Number Generator (PRNG) vulnerability in Apache StreamPipes user self-registration and password recovery mechanism.
This allows an attacker to guess the recovery token in a reasonable time and thereby to take over the attacked user's account.
This issue affects Apache StreamPipes: from 0.69.0 through 0.93.0.

Users are recommended to upgrade to version 0.95.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29868
- https://github.com/apache/streampipes/commit/1d94191c49617dffbcb6f6d8fd73bcd5dd597d52
- https://github.com/apache/streampipes
- https://lists.apache.org/thread/g7t7zctvq2fysrw1x17flnc12592nhx7
- http://www.openwall.com/lists/oss-security/2024/06/22/1
