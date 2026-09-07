# [M] Umbraco CMS XXE Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h2vq-7gf2-qw9v
CVE: CVE-2017-15280
CWE: CWE-611
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-h2vq-7gf2-qw9v
Type: github-advisory

## Affected
- NuGet: `UmbracoCms.Web` — affected >=0 <7.7.3

## Details
XML external entity (XXE) vulnerability in Umbraco CMS before 7.7.3 allows attackers to obtain sensitive information by reading files on the server or sending TCP requests to intranet hosts (aka SSRF), related to `Umbraco.Web/umbraco.presentation/umbraco/dialogs/importDocumenttype.aspx.cs`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15280
- https://github.com/umbraco/Umbraco-CMS/commit/5dde2efe0d2b3a47d17439e03acabb7ea2befb64
- https://github.com/umbraco/Umbraco-CMS
- https://github.com/umbraco/Umbraco-CMS/blob/release-7.7.3/src/Umbraco.Web/Umbraco.Web.csproj
- http://issues.umbraco.org/issue/U4-10506
