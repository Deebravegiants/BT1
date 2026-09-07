# [M] OWASP.AntiSamy mXSS when preserving comments

## Summary
Severity: Medium
Advisory: GHSA-8x6f-956f-q43w
CVE: CVE-2023-51652
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-02
Source: https://github.com/advisories/GHSA-8x6f-956f-q43w
Type: github-advisory

## Affected
- NuGet: `OWASP.AntiSamy` — affected >=0 <1.2.0

## Details
# Impact

There is a potential for a mutation XSS (mXSS) vulnerability in AntiSamy caused by flawed parsing of the HTML being sanitized. To be subject to this vulnerability the `preserveComments` directive must be enabled in your policy file and also allow for certain tags at the same time. As a result, certain crafty inputs can result in elements in comment tags being interpreted as executable when using AntiSamy's sanitized output.

# Patches

Patched in OWASP AntiSamy .NET 1.2.0 and later. See important remediation details in the reference given below.

# Workarounds

If you cannot upgrade to a fixed version of the library, the following mitigation can be applied until you can upgrade: Manually edit your AntiSamy policy file (e.g., antisamy.xml) by deleting the `preserveComments` directive or setting its value to `false`,  if present. Also it would be useful to make AntiSamy remove the `noscript` tag by adding this in your tag definitions under the `<tagrules>` node (or deleting it entirely if present):
```xml
<tag name="noscript" action="remove"/>
```

As the previously mentioned policy settings are preconditions for the mXSS attack to work, changing them as recommended should be sufficient to protect you against this vulnerability when using a vulnerable version of this library. However, the existing bug would still be present in AntiSamy or its parser dependency (HtmlAgilityPack). The safety of this workaround relies on configurations that may change in the future and don't address the root cause of the vulnerability. As such, it is strongly recommended to upgrade to a fixed version of AntiSamy.

# For more information

If you have any questions or comments about this advisory:

Email one of the project co-leaders, listed on the [OWASP AntiSamy project](https://owasp.org/www-project-antisamy/) page, under "Leaders".

## References
- https://github.com/spassarop/antisamy-dotnet/security/advisories/GHSA-8x6f-956f-q43w
- https://nvd.nist.gov/vuln/detail/CVE-2023-51652
- https://github.com/spassarop/antisamy-dotnet/commit/7e500daef6ad9c10e97c68feab78f4cb6e3083c6
- https://github.com/spassarop/antisamy-dotnet/commit/8117911933e75a25cd0054ef017577486338444a
- https://github.com/spassarop/antisamy-dotnet
