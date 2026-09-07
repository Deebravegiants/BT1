# [M] Malicious input can provoke XSS when preserving comments

## Summary
Severity: Medium
Advisory: GHSA-2mrq-w8pv-5pvq
CVE: CVE-2024-23635
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-02
Source: https://github.com/advisories/GHSA-2mrq-w8pv-5pvq
Type: github-advisory

## Affected
- Maven: `org.owasp.antisamy:antisamy` — affected >=0 <1.7.5

## Details
# Impact

There is a potential for a mutation XSS (mXSS) vulnerability in AntiSamy caused by flawed parsing of the HTML being sanitized. To be subject to this vulnerability the `preserveComments` directive must be enabled in your policy file. As a result, certain crafty inputs can result in elements in comment tags being interpreted as executable when using AntiSamy's sanitized output.

# Patches

Patched in AntiSamy 1.7.5 and later. This is due to parsing behavior in the [neko-htmlunit](https://github.com/HtmlUnit/htmlunit-neko) dependency, just by updating to a newer version the issue was solved. See important remediation details in the reference given below.

# Workarounds

If you cannot upgrade to a fixed version of the library, the following mitigation can be applied until you can upgrade: Manually edit your AntiSamy policy file (e.g., antisamy.xml) by deleting the `preserveComments` directive or setting its value to `false`,  if present.

As the previously mentioned policy settings are preconditions for the mXSS attack to work, changing them as recommended should be sufficient to protect you against this vulnerability when using a vulnerable version of this library. However, the existing bug would still be present in the parser dependency (neko-htmlunit) and therefore in AntiSamy. The safety of this workaround relies on configurations that may change in the future and don't address the root cause of the vulnerability. As such, it is strongly recommended to upgrade to a fixed version of AntiSamy.

# For more information

If you have any questions or comments about this advisory:

Email one of the project co-leaders, listed on the [OWASP AntiSamy project](https://owasp.org/www-project-antisamy/) page, under "Leaders".

## References
- https://github.com/nahsra/antisamy/security/advisories/GHSA-2mrq-w8pv-5pvq
- https://nvd.nist.gov/vuln/detail/CVE-2024-23635
- https://github.com/nahsra/antisamy/commit/12a2e31d3855430c119480655c2bbbbb79a66ecd
- https://github.com/nahsra/antisamy/commit/3e84410ed06ab67f0a4cc3183c67528210f4847d
- https://github.com/nahsra/antisamy
