# [M] Umbraco has Stored XSS in UFM Rendering Pipeline via Permissive DOMPurify Attribute Filtering

## Summary
Severity: Medium
Advisory: GHSA-vrqc-59mw-qqg7
CVE: CVE-2026-31833
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-vrqc-59mw-qqg7
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=16.2.0 <16.5.1
- NuGet: `Umbraco.Cms` — affected >=17.0.0 <17.2.2

## Details
### Description
An authenticated backoffice user with access to Settings can inject malicious HTML into property type descriptions. Due to an overly permissive `attributeNameCheck` configuration (/.+/) in the UFM DOMPurify instance, event handler attributes such as onclick and onload, when used within Umbraco web components (`umb-*`, `uui-*`, `ufm-*`) were not filtered.

### Impact
As property type descriptions support Markdown/HTML via the UFM rendering pipeline, injected event handlers are rendered in the backoffice interface, resulting in a stored XSS affecting other backoffice users.

### Patches
The issue is patched in 16.5.1 and 17.2.2.

### Workarounds
There is no workaround other than upgrading.

### References
https://docs.umbraco.com/umbraco-cms/reference/umbraco-flavored-markdown

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-vrqc-59mw-qqg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-31833
- https://github.com/umbraco/Umbraco-CMS
