# [C] Orval: Import-time RCE via schema property name -> computed-property-key injection in the zod client

## Summary
Severity: Critical
Advisory: GHSA-6mr6-jvcr-2f25
CVE: CVE-2026-71866
CWE: CWE-89, CWE-95
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-6mr6-jvcr-2f25
Type: github-advisory

## Affected
- npm: `orval` — affected >=0 <8.21.0

## Details
### Summary

orval's zod client emits each schema property name as a double-quoted key in the generated zod.object({...})
WITHOUT escaping the double quote. A " in a property name closes the key and lands in object-literal
context, where an injected computed property key [expr] is evaluated when zod.object({...}) runs -- which
is at MODULE IMPORT (the `export const X = zod.object({...})` executes on load) -> import-time RCE. The
property name is a pure data field. Verified on orval 8.19.0 / Node. CWE-94 / CWE-95 / CWE-116.

### Details

```ts
export const OpBody = zod.object({ "a":zod.string(),[require("fs").writeFileSync("PWNED","")]:zod.string(),"b": zod.string().optional() })
```

Sibling: the MSW mock uses a single-quoted key (' breakout, call-time) -- separate report. The TS interface
key is a type (DoS only). Distinct from orval's $ref / route-path / server-url / zod-default findings.

### PoC

reproduce.sh (+ make_spec.py) attached: a property name a":zod.string(),[require("fs").writeFileSync("<marker>","")]:zod.string(),"b
-> zod.object; evaluating it (= importing the module) writes the marker. Verified on 8.19.0.

### Impact

JavaScript / OS command execution (via child_process) at import time for anyone who generates an orval zod
client from an attacker-controlled spec and imports it. Estimated Critical, e.g.
`CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N`.

### Suggested fix

Escape the property name for the JS string key (JSON.stringify) in the zod.object key generation; never
interpolate a raw property name adjacent to [ ] in object-literal position.
[maintainer-report.txt](https://github.com/user-attachments/files/29426038/maintainer-report.txt)
[make_spec.py](https://github.com/user-attachments/files/29426039/make_spec.py)
[reproduce.sh](https://github.com/user-attachments/files/29426040/reproduce.sh)

## References
- https://github.com/orval-labs/orval/security/advisories/GHSA-6mr6-jvcr-2f25
- https://nvd.nist.gov/vuln/detail/CVE-2026-71866
- https://github.com/orval-labs/orval/pull/3692
- https://github.com/orval-labs/orval/commit/8ef1bfdf3f9bcaf9dabfbe2e42887f1c0e159ab6
- https://github.com/orval-labs/orval
- https://github.com/orval-labs/orval/releases/tag/v8.21.0
