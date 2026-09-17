# [H] dotCMS allows remote authenticated users to execute arbitrary Java code

## Summary
Severity: High
Advisory: GHSA-42vg-q6mw-cfh5
CVE: CVE-2012-1826
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-42vg-q6mw-cfh5
Type: github-advisory

## Affected
- Maven: `com.dotcms:dotcms` — affected >=1.9 <1.9.5.1

## Details
dotCMS 1.9 before 1.9.5.1 allows remote authenticated users to execute arbitrary Java code via a crafted (1) XSLT or (2) Velocity template.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1826
- https://github.com/dotCMS/dotCMS/issues/261
- https://github.com/dotCMS/dotCMS/issues/281
- https://github.com/dotCMS/dotCMS
- https://web.archive.org/web/20201208044614/https://gist.github.com/jtesser/2627440
- https://web.archive.org/web/20210124000108/https://www.securityfocus.com/bid/53688
- http://dotcms.com/dotCMSVersions
- http://www.kb.cert.org/vuls/id/898083
