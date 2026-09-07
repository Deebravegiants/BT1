# [M] mXSS in AntiSamy

## Summary
Severity: Medium
Advisory: GHSA-pcf2-gh6g-h5r2
CVE: CVE-2023-43643
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-09
Source: https://github.com/advisories/GHSA-pcf2-gh6g-h5r2
Type: github-advisory

## Affected
- Maven: `org.owasp.antisamy:antisamy` — affected >=0 <1.7.4

## Details
# Impact

There is a potential for a mutation XSS (mXSS) vulnerability in AntiSamy caused by flawed parsing of the HTML being sanitized. To be subject to this vulnerability the `preserveComments` directive must be enabled in your policy file and also allow for certain tags at the same time. As a result, certain crafty inputs can result in elements in comment tags being interpreted as executable when using AntiSamy's sanitized output.

# Patches

Patched in AntiSamy 1.7.4 and later. See important remediation details in the reference given below.

# Workarounds

If you cannot upgrade to a fixed version of the library, the following mitigation can be applied until you can upgrade: Manually edit your AntiSamy policy file (e.g., antisamy.xml) by deleting the `preserveComments` directive or setting its value to `false`,  if present. Also it would be useful to make AntiSamy remove the `noscript` tag by adding this in your tag definitions under the `<tagrules>` node (or deleting it entirely if present):
```xml
<tag name="noscript" action="remove"/>
```

As the previously mentioned policy settings are preconditions for the mXSS attack to work, changing them as recommended should be sufficient to protect you against this vulnerability when using a vulnerable version of this library. However, the existing bug would still be present in AntiSamy or its parser dependency (neko-htmlunit). The safety of this workaround relies on configurations that may change in the future and don't address the root cause of the vulnerability. As such, it is strongly recommended to upgrade to a fixed version of AntiSamy.

# For more information

If you have any questions or comments about this advisory:

Email one of the project co-leaders, listed on the [OWASP AntiSamy project](https://owasp.org/www-project-antisamy/) page, under "Leaders".

## References
- https://github.com/nahsra/antisamy/security/advisories/GHSA-pcf2-gh6g-h5r2
- https://nvd.nist.gov/vuln/detail/CVE-2023-43643
- https://github.com/nahsra/antisamy
- https://github.com/nahsra/antisamy/releases/tag/v1.7.4
