# [M] Incorrect Default Permissions in JetBrains Kotlin

## Summary
Severity: Medium
Advisory: GHSA-cqj8-47ch-rvvq
CVE: CVE-2020-29582
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cqj8-47ch-rvvq
Type: github-advisory

## Affected
- Maven: `org.jetbrains.kotlin:kotlin-stdlib` — affected >=0 <1.4.21

## Details
In JetBrains Kotlin before 1.4.21, a vulnerable Java API was used for temporary file and folder creation. An attacker was able to read data from such files and list directories due to insecure permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29582
- https://blog.jetbrains.com
- https://blog.jetbrains.com/blog/2021/02/03/jetbrains-security-bulletin-q4-2020
- https://lists.apache.org/thread.html/r2721aba31a8562639c4b937150897e24f78f747cdbda8641c0f659fe@%3Cusers.kafka.apache.org%3E
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
