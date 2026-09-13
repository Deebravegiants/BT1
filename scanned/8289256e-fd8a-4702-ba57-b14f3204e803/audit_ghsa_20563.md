# [C] RCE in Mingsoft MCMS

## Summary
Severity: Critical
Advisory: GHSA-8wq7-hhjj-fpqv
CVE: CVE-2022-22930
CWE: CWE-1336
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-22
Source: https://github.com/advisories/GHSA-8wq7-hhjj-fpqv
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0 <5.2.9

## Details
A remote code execution (RCE) vulnerability in the Template Management function of MCMS allows attackers to execute arbitrary code via a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22930
- https://github.com/ming-soft/MCMS/issues/98
- https://web.archive.org/web/20220201022121/https://gitee.com/mingSoft/MCMS/issues/I4Q4M6
