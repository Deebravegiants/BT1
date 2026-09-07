# [H] MCMS vulnerable to arbitrary code execution via crafted thumbnail

## Summary
Severity: High
Advisory: GHSA-293v-5329-36wp
CVE: CVE-2020-22755
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-08
Source: https://github.com/advisories/GHSA-293v-5329-36wp
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0

## Details
File upload vulnerability in MCMS 5.0 allows attackers to execute arbitrary code via a crafted thumbnail. A different vulnerability than CVE-2022-31943.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-22755
- https://github.com/ming-soft/MCMS/issues/42
- https://github.com/ming-soft/MCMS
