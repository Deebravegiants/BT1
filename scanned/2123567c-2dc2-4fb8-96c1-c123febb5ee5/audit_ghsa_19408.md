# [H] ses's global contour bindings leak into Compartment lexical scope

## Summary
Severity: High
Advisory: GHSA-h9w6-f932-gq62
CVE: CVE-2025-32792
CWE: CWE-497
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-18
Source: https://github.com/advisories/GHSA-h9w6-f932-gq62
Type: github-advisory

## Affected
- npm: `ses` — affected >=0 <1.12.0

## Details
### Impact

Web pages and web extensions using `ses` and the `Compartment` API to evaluate third-party code in an isolated execution environment that have also elsewhere used `const`, `let`, and `class` bindings in the top-level scope of a `<script>` tag will have inadvertently revealed these bindings in the lexical scope of third-party code.

### Patches

This compromise is addressed in `ses` version `1.12.0`. The mechanism for confining third-party code involves a `with` block and a semi-opaque scope `Proxy`. The proxy previously revealed any named property to the surrounding lexical scope if it were absent on `globalThis`, so that the third-party code would receive an informative `ReferenceError`, relying on the invalid assumption that only properties of `globalThis` are in the top-level lexical scope. The solution makes the scope proxy fully opaque. Consequently, accessing an unbound free lexical name will produce `undefined` instead of throwing `ReferenceError`.
Assigning to an unbound free lexical name will continue to throw a `ReferenceError`.

### Workarounds

This problem can be mitigated either by avoiding top-level `let`, `const`, or `class` bindings in `<script>` tags, which is an existing industry best-practice, or change these to `var` bindings to be reflected on `globalThis`, or upgrade `ses` to version `1.12.0` or greater.

Some bundlers by default transform top-level `let`, `const`, and `class` bindings to `var`.

### Disclosure

This vulnerability was disclosed by @mingijunggrape in the course of their studies at UNIST (Ulsan National Institute of Science and Technology) as a member of the Web Security Lab (https://websec-lab.github.io/).

## References
- https://github.com/endojs/endo/security/advisories/GHSA-h9w6-f932-gq62
- https://nvd.nist.gov/vuln/detail/CVE-2025-32792
- https://github.com/endojs/endo
