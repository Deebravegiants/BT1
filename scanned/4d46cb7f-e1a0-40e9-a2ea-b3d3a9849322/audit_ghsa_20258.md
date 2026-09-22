# [H] Insufficiently Protected Credentials in PowerJob

## Summary
Severity: High
Advisory: GHSA-w4q4-jcm7-g4m6
CVE: CVE-2020-28865
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-w4q4-jcm7-g4m6
Type: github-advisory

## Affected
- Maven: `com.github.kfcfans:powerjob` — affected >=0 <3.3.3

## Details
An issue was discovered in PowerJob through 3.2.2, allows attackers to change arbitrary user passwords via the id parameter to /appinfo/save.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28865
- https://github.com/KFCFans/PowerJob/issues/99
- https://github.com/PowerJob/PowerJob/commit/464ce2dc0ca3e65fa1dc428239829890c52a413a
- https://github.com/PowerJob/PowerJob
