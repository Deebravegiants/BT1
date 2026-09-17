# [H] Bolt CMS Server-Side Template Injection via Unsandboxed allow_twig Field Rendering

## Summary
Severity: High
Advisory: CVE-2026-71291
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71291
Type: osv

## Details
Bolt CMS renders content field values through Twig's full application-level Environment with no SandboxExtension registered anywhere in the codebase. In src/Entity/Field.php, getTwigValue calls shouldBeRenderedAsTwig, which gates rendering only on the field definition's allow_twig flag and a regex checking for , , or ; when true, the raw field value is compiled and rendered via with no sandboxing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71291.json
- https://github.com/bolt/core
- https://github.com/bolt/core/blob/6.1/src/Entity/Field.php
- https://nvd.nist.gov/vuln/detail/CVE-2026-71291
