# [H] TOON: Prototype pollution when decoding untrusted TOON input

## Summary
Severity: High
Advisory: CVE-2026-82404
Aliases: GHSA-p95v-992w-h6c3
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-82404
Type: osv

## Details
TOON is a compact, human-readable serialization of JSON data for LLM prompts. Prior to 2.3.1, decoding attacker-controlled TOON with a __proto__, constructor, or prototype key wrote through the object prototype chain instead of creating an own property, polluting Object.prototype for the runtime. In packages/toon/src/decode/expand.ts, the expandPaths: 'safe' path and insertPathSafe function made dotted keys such as a.__proto__.x the strongest vector, while plain nested objects, tabular rows, quoted keys, and streaming decode were also affected. The encoder also dropped own __proto__ properties and could invoke an inherited setter during normalization. Services that decode untrusted TOON could experience denial of service or, when a suitable downstream gadget is present, remote code execution. This issue is fixed in version 2.3.1.

## References
- https://github.com/toon-format/toon/releases/tag/v2.3.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82404.json
- https://github.com/toon-format/toon/security/advisories/GHSA-p95v-992w-h6c3
- https://nvd.nist.gov/vuln/detail/CVE-2026-82404
- https://github.com/toon-format/toon/commit/94a2b7560b2b5ed903a4d466a3bce8b13daa2660
- https://github.com/toon-format/toon/pull/316
