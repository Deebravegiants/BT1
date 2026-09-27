# [H] exceljs through 4.4.0 Prototype Pollution via deepMerge Reached From Note Serialization

## Summary
Severity: High
Advisory: CVE-2026-78207
Aliases: GHSA-qwr4-7h29-chpf
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78207
Type: osv

## Details
exceljs through 4.4.0 contains a prototype pollution vulnerability in the deepMerge helper that fails to reject __proto__, constructor, or prototype keys when merging note objects. Attackers can assign parsed JSON with a malicious __proto__ property to cell notes, modifying Object.prototype and affecting all plain objects created in the process.

## References
- https://www.npmjs.com/package/exceljs
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78207.json
- https://github.com/mateocallec/exceljs-hardened/security/advisories/GHSA-qwr4-7h29-chpf
- https://nvd.nist.gov/vuln/detail/CVE-2026-78207
- https://www.vulncheck.com/advisories/exceljs-through-prototype-pollution-via-deepmerge-reached-from-note-serialization
- https://github.com/exceljs/exceljs
- https://github.com/exceljs/exceljs/blob/v4.4.0/lib/utils/under-dash.js#L155-L181
