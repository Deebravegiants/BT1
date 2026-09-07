# [H] PowerJob incorrect access control vulnerability

## Summary
Severity: High
Advisory: GHSA-443m-3fr6-w8wj
CVE: CVE-2023-36106
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-17
Source: https://github.com/advisories/GHSA-443m-3fr6-w8wj
Type: github-advisory

## Affected
- Maven: `tech.powerjob:powerjob` — affected >=0

## Details
An incorrect access control vulnerability in powerjob 4.3.2 and earlier allows remote attackers to obtain sensitive information via the interface for querying via `appId` parameter to `/container/list`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-36106
- https://gist.github.com/tztdsb/a653b6db328199ec0f55e54b4e466415#file-gistfile1-txt
- https://gitee.com/KFCFans/PowerJob
