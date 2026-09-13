# [H] Readest: unsanitized iframe srcdoc attribute in the EPUB sanitizer can lead to arbitrary code execution

## Summary
Severity: High
Advisory: CVE-2026-82642
Aliases: GHSA-p4x7-pf2c-xrvj
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-82642
Type: osv

## Details
Readest is an open-source e-book reader built on Tauri. In versions prior to 0.11.16, EPUB chapter HTML is sanitized with DOMPurify using a configuration that forbade only the <script> tag (FORBID_TAGS: ['script']) in apps/readest-app/src/services/transformers/sanitizer.ts. DOMPurify does not parse the contents of the srcdoc attribute on <iframe> elements, treating it as an opaque string attribute, so an attacker who can get an <iframe> element to survive sanitization can embed a complete HTML document containing a <script> tag inside srcdoc and have it execute when the browser renders the iframe. The content iframe is configured with sandbox="allow-same-origin allow-scripts", so script executing inside it shares the parent origin and can reach parent.parent.__TAURI_INTERNALS__.invoke(...), giving access to every Tauri IPC command the application is permitted to use, which escalates to arbitrary code execution. The payload can be made invisible (zero-size, transparent iframe) so the reader sees only normal book text. Version 0.11.16 hardened the sanitizer configuration by adding 'iframe', 'object' and 'embed' to FORBID_TAGS and adding 'srcdoc' to FORBID_ATTR.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82642.json
- https://github.com/readest/readest/releases/tag/v0.11.16
- https://github.com/readest/readest/security/advisories/GHSA-p4x7-pf2c-xrvj
- https://nvd.nist.gov/vuln/detail/CVE-2026-82642
- https://github.com/readest/readest/commit/005aa2d6157a34049bf45641c06861d606a85edb
- https://github.com/readest/readest/pull/4762
- https://github.com/readest/readest
