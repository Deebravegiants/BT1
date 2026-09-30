# [C] Alluxio vulnerable to arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-xrrh-h86w-pwfj
CVE: CVE-2023-38889
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-15
Source: https://github.com/advisories/GHSA-xrrh-h86w-pwfj
Type: github-advisory

## Affected
- Maven: `org.alluxio:alluxio-parent` — affected >=0

## Details
An issue in Alluxio v.2.9.3 and before allows an attacker to execute arbitrary code via a crafted script to the username parameter of lluxio.util.CommonUtils.getUnixGroups(java.lang.String).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38889
- https://github.com/Alluxio/alluxio/issues/17766
- https://github.com/Alluxio/alluxio
