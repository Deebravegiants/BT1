# [M] Apache Linkis: Password Exposure

## Summary
Severity: Medium
Advisory: GHSA-6vfr-p2hx-6v32
CVE: CVE-2025-59355
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-19
Source: https://github.com/advisories/GHSA-6vfr-p2hx-6v32
Type: github-advisory

## Affected
- Maven: `org.apache.linkis:linkis-metadata` — affected >=1.0.0 <1.8.0

## Details
When org.apache.linkis.metadata.util.HiveUtils.decode() fails to perform Base64 decoding, it records the complete input parameter string in the log via logger.error(str + "decode failed", e). If the input parameter contains sensitive information such as Hive Metastore keys, plaintext passwords will be left in the log files when decoding fails, resulting in information leakage.


Affected Scope
Component: Sensitive fields in hive-site.xml (e.g., javax.jdo.option.ConnectionPassword) or other fields encoded in Base64.
Version: Apache Linkis 1.0.0 – 1.7.0


Trigger Conditions
The value of the configuration item is an invalid Base64 string.
Log files are readable by users other than hive-site.xml administrators.


Severity: Low
The probability of Base64 decoding failure is low.
The leakage is only triggered when logs at the Error level are exposed.

Remediation
Apache Linkis 1.8.0 and later versions have replaced the log with desensitized content.
logger.error("URL decode failed: {}", e.getMessage());   // 不再输出 str


Users are recommended to upgrade to version 1.8.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59355
- https://github.com/apache/linkis
- https://lists.apache.org/thread/4dcgmqdkk2p5y4k43ok5rgd4ylx8698h
- https://lists.apache.org/thread/75z7vhftw6w1mllndgpkfmcj0fzo4lbj
- http://www.openwall.com/lists/oss-security/2025/09/19/1
