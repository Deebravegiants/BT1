# [M] Hadoop token in temp file visible to all users in Apache Gobblin

## Summary
Severity: Medium
Advisory: GHSA-p435-w4xm-jj8x
CVE: CVE-2021-36151
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-06
Source: https://github.com/advisories/GHSA-p435-w4xm-jj8x
Type: github-advisory

## Affected
- Maven: `org.apache.gobblin:gobblin-core` — affected >=0 <0.16.0

## Details
In Apache Gobblin, the Hadoop token is written to a temp file that is visible to all local users on Unix-like systems. This affects versions <= 0.15.0. Users should update to version 0.16.0 which addresses this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36151
- https://lists.apache.org/thread/3cdkyxdd6xk05lsvr3l66dsnvhwyo1t0
