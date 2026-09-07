# [M] Umbraco CMS Vulnerable to Stored XSS on Content Page Through Markdown Editor Preview Pane

## Summary
Severity: Medium
Advisory: GHSA-gvpc-3pj6-4m9w
CVE: CVE-2024-35218
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-gvpc-3pj6-4m9w
Type: github-advisory

## Affected
- NuGet: `UmbracoCms.Core` — affected >=8.0.0 <8.18.13
- NuGet: `UmbracoCms.Core` — affected >=10.0.0 <10.8.4
- NuGet: `UmbracoCms.Core` — affected >=12.0.0 <12.3.7
- NuGet: `UmbracoCms.Core` — affected >=13.0.0 <13.1.1

## Details
### Impact
Stored Cross-site scripting (XSS) enable attackers that have access to backoffice to bring malicious content into a website or application.

### Affected versions
Umbraco CMS >= 8.00

### Patches
This is fixed in 8.18.13, 10.8.4, 12.3.7, 13.1.1 by implementing IHtmlSanitizer

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-gvpc-3pj6-4m9w
- https://nvd.nist.gov/vuln/detail/CVE-2024-35218
- https://github.com/umbraco/Umbraco-CMS/commit/1b712fe6ec52aa4e71b3acf63e393c8e6ab85385
- https://github.com/umbraco/Umbraco-CMS/commit/a2684069b1e9976444f60b4b37a80be05b87f6b6
- https://github.com/umbraco/Umbraco-CMS/commit/cbf9f9bcd199d7ca0412be3071d275556f10b7ba
- https://github.com/umbraco/Umbraco-CMS/commit/d090176272d07500dac0daee7c598aa8bb321050
- https://github.com/umbraco/Umbraco-CMS
