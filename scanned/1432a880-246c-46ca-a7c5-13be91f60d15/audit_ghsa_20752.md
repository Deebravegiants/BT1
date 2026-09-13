# [H] Improper Privilege Management in com.xuxueli:xxl-job

## Summary
Severity: High
Advisory: GHSA-7qq9-9g2w-56f9
CVE: CVE-2022-36157
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-20
Source: https://github.com/advisories/GHSA-7qq9-9g2w-56f9
Type: github-advisory

## Affected
- Maven: `com.xuxueli:xxl-job` — affected >=0 <2.4.0

## Details
XXL-JOB all versions as of 11 July 2022 are vulnerable to Insecure Permissions resulting in the ability to execute admin function with low Privilege account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36157
- https://github.com/Richard-Muzi/vulnerability/issues/1
- https://github.com/xuxueli/xxl-job/commit/730c1066b80e8ab44503ed34ced19ef8e0471fec
- https://github.com/xuxueli/xxl-job
