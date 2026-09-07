# [M] Alluxio Cross Site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-298m-hvgh-x9cw
CVE: CVE-2020-21485
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-298m-hvgh-x9cw
Type: github-advisory

## Affected
- Maven: `org.alluxio:alluxio-parent` — affected >=0

## Details
Cross Site Scripting vulnerability in Alluxio v.1.8.1 allows a remote attacker to executea arbitrary code via the path parameter in the browse board component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-21485
- https://github.com/Alluxio/alluxio/issues/10552
- https://github.com/Alluxio/alluxio
