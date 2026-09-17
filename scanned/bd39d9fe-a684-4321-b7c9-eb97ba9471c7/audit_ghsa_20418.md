# [C] Arbitrary File Upload in Mingsoft MCMS

## Summary
Severity: Critical
Advisory: GHSA-77hh-p7r6-66pv
CVE: CVE-2022-22929
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-22
Source: https://github.com/advisories/GHSA-77hh-p7r6-66pv
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0

## Details
MCMS v5.2.4 was discovered to have an arbitrary file upload vulnerability in the New Template module, which allows attackers to execute arbitrary code via a crafted ZIP file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22929
- https://web.archive.org/web/20230521040336/https://gitee.com/mingSoft/MCMS/issues/I4Q4NV
