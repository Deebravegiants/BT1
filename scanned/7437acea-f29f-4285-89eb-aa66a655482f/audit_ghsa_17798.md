# [M] Apache Hive vulnerable to Observable Timing Discrepancy and Authentication Bypass by Spoofing

## Summary
Severity: Medium
Advisory: GHSA-p953-3j66-hg45
CVE: CVE-2024-23953
CWE: CWE-208, CWE-290
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-01-28
Source: https://github.com/advisories/GHSA-p953-3j66-hg45
Type: github-advisory

## Affected
- Maven: `org.apache.hive:hive-llap-common` — affected >=0 <4.0.0

## Details
Use of Arrays.equals() in LlapSignerImpl in Apache Hive to compare message signatures allows attacker to forge a valid signature for an arbitrary message byte by byte. The attacker should be an authorized user of the product to perform this attack. Users are recommended to upgrade to version 4.0.0, which fixes this issue.

The problem occurs when an application doesn’t use a constant-time algorithm for validating a signature. The method Arrays.equals() returns false right away when it sees that one of the input’s bytes are different. It means that the comparison time depends on the contents of the arrays. This little thing may allow an attacker to forge a valid signature for an arbitrary message byte by byte. So it might allow malicious users to submit splits/work with selected signatures to LLAP without running as a privileged user, potentially leading to DDoS attack.

More details in the reference section.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23953
- https://github.com/apache/hive/commit/b418e3c9f479ba8e7d31e6470306111002ffa809
- https://blog.gypsyengineer.com/en/security/preventing-timing-attacks-with-codeql.html
- https://cqr.company/web-vulnerabilities/timing-attacks
- https://github.com/apache/hive
- https://issues.apache.org/jira/browse/HIVE-28030
- https://lists.apache.org/thread/0nloywj49nbtlc6l3c6363qvq7o1ztb7
- http://www.openwall.com/lists/oss-security/2025/01/28/3
