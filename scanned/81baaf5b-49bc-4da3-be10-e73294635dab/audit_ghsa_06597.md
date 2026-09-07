# [M] plone.app.textfield: Stored XSS by spoofing mime type 

## Summary
Severity: Medium
Advisory: GHSA-4r4f-gg25-rmg5
CVE: CVE-2026-54503
CWE: CWE-80
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-4r4f-gg25-rmg5
Type: github-advisory

## Affected
- PyPI: `plone.app.textfield` — affected >=0 <2.0.2
- PyPI: `plone.app.textfield` — affected >=3.0.0 <3.0.2
- PyPI: `plone.app.textfield` — affected >=4.0.0 <4.0.1

## Details
### Impact

A stored XSS affecting RichText fields. RichTextValue.output returns the raw, unsanitized stored value whenever the stored mimeType equals the outputMimeType. Because the safe-HTML output type (`text/x-html-safe`) is the type that signifies "already sanitized", any value whose stored mimeType equals it bypasses the safe_html transform entirely on render. The transform itself is sound — it correctly strips `on*` event-handler attributes and `javascript:/data:` URIs; the defect is that it is never invoked for these values. The unsanitized value is then emitted via `tal:content="structure ..."`, which performs no escaping, so the payload executes in the viewer's browser. 

This can be a problem when a RichText field is wrongly defined in code with a `mimeType` and `outputMimeType` that are the same, or when the REST API is used to the same effect.

### Patches
The problem has been patched:

* For Plone 6.0, upgrade `plone.app.textfield` to 2.0.2.
* For Plone 6.1, upgrade `plone.app.textfield` to 3.0.2.
* For Plone 6.2, upgrade `plone.app.textfield` to 4.0.1.

### Workarounds
There is no known workaround.

## References
- https://github.com/plone/plone.app.textfield/security/advisories/GHSA-4r4f-gg25-rmg5
- https://github.com/plone/plone.app.textfield
