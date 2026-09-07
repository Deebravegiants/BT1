# [H] Edit template, Remote Code Execution (RCE) Vulnerability in Latest Release 4.4.0

## Summary
Severity: High
Advisory: GHSA-6fmv-q269-55cw
CVE: CVE-2020-15277
CWE: CWE-434, CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-10-30
Source: https://github.com/advisories/GHSA-6fmv-q269-55cw
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=4.4.0 <4.4.1

## Details
baserCMS 4.4.0 and earlier is affected by Remote Code Execution (RCE).

Impact: XSS via Arbitrary script execution.
Attack vector is: Administrator must be logged in.
Components are: Edit template.
Tested baserCMS Version : 4.4.0 (Latest)
Affected baserCMS Version : 4.0.0 ~ 4.4.0
Patches : https://basercms.net/security/20201029
Found by Aquilao Null

## References
- https://github.com/baserproject/basercms/security/advisories/GHSA-6fmv-q269-55cw
- https://nvd.nist.gov/vuln/detail/CVE-2020-15277
- https://github.com/baserproject/basercms/commit/bb027c3967b0430adcff2d2fedbc23d39077563b
- https://basercms.net/security/20201029
