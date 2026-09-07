# [M] earmark: Stored XSS via unescaped HTML attribute values

## Summary
Severity: Medium
Advisory: GHSA-52mm-h59v-f3c7
CVE: CVE-2026-48591
CWE: CWE-79, CWE-83
Ecosystem: Hex
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-52mm-h59v-f3c7
Type: github-advisory

## Affected
- Hex: `earmark` — affected >=1.4.1

## Details
Improper Neutralization of Script in Attributes in a Web Page vulnerability in pragdave earmark allows stored cross-site scripting via unescaped HTML attribute values.

'Elixir.Earmark.Transform':_make_att1/2 in lib/earmark/transform.ex splices attribute values verbatim between two literal " bytes: [" ", name, "=\"", value, "\""]. Text nodes are routed through the existing escape function which encodes " as &quot;, but attribute values never visit that path. A markdown link whose URL or title contains a bare " closes the attribute early and lets the trailing bytes be parsed by the browser as fresh HTML attributes. For example, [click](http://example.com/?a=x" onerror="alert(1)) renders as <a href="http://example.com/?a=x" onerror="alert(1)">click</a>, executing arbitrary JavaScript in the victim's browser.

The earmark library is no longer maintained and has been retired on Hex. No patched version will be released. All releases from 1.4.1 onward are affected, and users should migrate to a maintained Markdown library such as MDEx.

This issue affects earmark from 1.4.1 onward.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48591
- https://cna.erlef.org/cves/CVE-2026-48591.html
- https://github.com/pragdave/earmark
- https://osv.dev/vulnerability/EEF-CVE-2026-48591
