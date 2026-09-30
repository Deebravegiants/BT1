# [M] ember-dynamic-render-template Client-Side Template Injection via Unsanitized templateString

## Summary
Severity: Medium
Advisory: CVE-2026-71286
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71286
Type: osv

## Details
The render-template component of ember-dynamic-render-template (addon/components/render-template.js) passes its property directly into Ember/Glimmer's compileTemplate (from @ember/template-compilation) with no sanitization, allow-listing, or validation of the input.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71286.json
- https://github.com/miguelcobain/ember-dynamic-render-template
- https://github.com/miguelcobain/ember-dynamic-render-template/blob/master/addon/components/render-template.js
- https://nvd.nist.gov/vuln/detail/CVE-2026-71286
