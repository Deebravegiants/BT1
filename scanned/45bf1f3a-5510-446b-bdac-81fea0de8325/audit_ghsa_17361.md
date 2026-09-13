# [H] XWiki vulnerable to remote code execution through insufficient protection against {{/html}} injection

## Summary
Severity: High
Advisory: GHSA-9xc6-c2rm-f27p
CVE: CVE-2025-66474
CWE: CWE-94, CWE-95
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-9xc6-c2rm-f27p
Type: github-advisory

## Affected
- Maven: `org.xwiki.rendering:xwiki-rendering-xml` — affected >=0 <16.10.10
- Maven: `org.xwiki.rendering:xwiki-rendering-xml` — affected >=17.0.0-rc-1 <17.4.3
- Maven: `org.xwiki.rendering:xwiki-rendering-xml` — affected >=17.5.0-rc-1 <17.6.0-rc-1

## Details
### Impact
Any user who can edit their own user profile or any other document can execute arbitrary script macros including Groovy and Python macros that allow remote code execution including unrestricted read and write access to all wiki contents. The reason is that rendering output is included as content of HTML macros with insufficient escaping, and it is thus possible to close the HTML macro and inject script macros that are executed with programming rights. To demonstrate, the content `{{html}}{{/html {{/html}}}}` can be inserted into any field of the user profile that supports wiki syntax like the "About" field. If this leads to the display of raw HTML, the instance is vulnerable.

### Patches
This problem has been patched by extending the escaping introduced by [XRENDERING-693](https://jira.xwiki.org/browse/XRENDERING-693) to also cover closing HTML macros that have spaces after the macro name in XWiki 16.10.10, 17.4.3 and 17.6.0RC1. A [similar fix](https://github.com/xwiki/xwiki-platform/commit/12b780ccd5bca5fc8f74f46648d7e02fa04fbc11) has been applied in `org.xwiki.platform:xwiki-platform-oldcore` as an extra safety net, see [XWIKI-23378](https://jira.xwiki.org/browse/XWIKI-23378). At this point, we're not aware that this extra safety net would be required for security.

The patch also fixes the injection of opening HTML macro syntaxes, e.g., with `{{html}}{{html{{/html}}}}` which disrupts the rendering of the user profile but for which we haven't found any further security impact apart from the disruption of the UI.

### Workarounds
We're not aware of any workarounds except for upgrading the affected module to a version with a fix.

## References
- https://github.com/xwiki/xwiki-rendering/security/advisories/GHSA-9xc6-c2rm-f27p
- https://nvd.nist.gov/vuln/detail/CVE-2025-66474
- https://github.com/xwiki/xwiki-platform/commit/12b780ccd5bca5fc8f74f46648d7e02fa04fbc11
- https://github.com/xwiki/xwiki-rendering/commit/9b71a2ee035815cfc29cebbfe81dbdd98f941d49
- https://github.com/xwiki/xwiki-rendering
- https://jira.xwiki.org/browse/XRENDERING-693
- https://jira.xwiki.org/browse/XRENDERING-792
- https://jira.xwiki.org/browse/XRENDERING-793
- https://jira.xwiki.org/browse/XWIKI-23378
