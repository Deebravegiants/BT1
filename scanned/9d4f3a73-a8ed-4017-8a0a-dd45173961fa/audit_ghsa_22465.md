# [H] Umbraco CMS vulnerable to CSRF

## Summary
Severity: High
Advisory: GHSA-5f6p-4hxq-rjxm
CVE: CVE-2015-8814
CWE: CWE-352
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5f6p-4hxq-rjxm
Type: github-advisory

## Affected
- NuGet: `Umbraco.CMS` — affected >=0 <7.4.0

## Details
Umbraco before 7.4.0 allows remote attackers to bypass anti-forgery security measures and conduct cross-site request forgery (CSRF) attacks as demonstrated by editing user account information in the `templates.asmx.cs` file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8814
- https://github.com/umbraco/Umbraco-CMS/commit/18c3345e47663a358a042652e697b988d6a380eb
- https://web.archive.org/web/20230608152113/https://issues.umbraco.org/issue/U4-7459
- http://www.openwall.com/lists/oss-security/2016/02/16/10
