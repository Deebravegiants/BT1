# [H] Preact has JSON VNode Injection issue

## Summary
Severity: High
Advisory: GHSA-36hm-qxxp-pg3m
CVE: CVE-2026-22028
CWE: CWE-843
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-36hm-qxxp-pg3m
Type: github-advisory

## Affected
- npm: `preact` — affected >=10.26.5 <10.26.10
- npm: `preact` — affected >=10.27.0 <10.27.3
- npm: `preact` — affected >=10.28.0 <10.28.2

## Details
## Impact

**Vulnerability Type:** HTML Injection via JSON Type Confusion

**Affected Versions:** Preact 10.26.5 through 10.28.1

**Severity:** Low to Medium (see below)

### Who is Impacted?

Applications using affected Preact versions are vulnerable if they meet **all** of the following conditions:

1. **Pass unmodified, unsanitized values** from user-modifiable data sources (APIs, databases, local storage, etc.) directly into the render tree
2. **Assume these values are strings** but the data source could return actual JavaScript objects instead of JSON strings
3. The data source either:
   - Fails to perform type sanitization **AND** blindly stores/returns raw objects interchangeably with strings, OR
   - Is compromised (e.g., poisoned local storage, filesystem, or database)

### Technical Details

Preact includes JSON serialization protection to prevent Virtual DOM elements from being constructed from arbitrary JSON. A regression introduced in Preact 10.26.5 caused this protection to be softened. In applications where values from JSON payloads are assumed to be strings and passed unmodified to Preact as children, a specially-crafted JSON payload could be constructed that would be incorrectly treated as a valid VNode. When this chain of failures occurs it can result in HTML injection, which can allow arbitrary script execution if not mitigated by CSP or other means.

**Important Notes:**
- This regression was never present in `preact-render-to-string`
- This is primarily an "expanded attack surface" issue rather than a standalone vulnerability
- Exploitation requires either insecure API design (no type validation) or a compromised data source

## Patches

**Patched Versions:**
- **10.26.10** (for 10.26.x users)
- **10.27.3** (for 10.27.x users)
- **10.28.2** (for 10.28.x users)

Users should upgrade to the latest patch version of whatever minor version they are on, which can be done via `npm update preact` or by installing one of the above versions directly.

The patch versions simply restore the previous strict equality checks that prevent JSON-parsed objects from being treated as valid VNodes.

## Mitigations

If you cannot upgrade immediately, implement the following mitigations:

- **Validate input types:** Don't accept arbitrary objects as inputs in your API and blindly store them. Enforce strict type contracts at API boundaries.
- **Cast or validate network data:** Don't assume strings are strings if your code got them from the network. Always cast to the expected type or validate before rendering.
- **Sanitize external data:** Validate that data from external sources (APIs, storage, databases) matches expected types before passing it to preact.
- **Use Content Security Policy (CSP):** Implement a strict CSP to prevent inline script execution as a defense-in-depth measure.

## References

- **Reporter:** [YoungGeun Choi](https://github.com/Xvezda)
- **Affected Versions:** 10.26.5 - 10.28.1
- **Patched Versions:** 10.26.10, 10.27.3, 10.28.2

## Credits

Preact thanks **YoungGeun Choi (Xvezda)** for the responsible disclosure of this vulnerability and for providing detailed reproduction steps and proof-of-concept demonstrations.

## Timeline

- **2026-01-04:** Initial vulnerability report received
- **2026-01-05:** Clarification requested regarding network/serialization boundary
- **2026-01-06:** Network PoC provided demonstrating real-world exploitatibility
- **2026-01-06:** Hotfix patches released (10.26.10, 10.27.3, 10.28.2)

---

**Recommendation:** All users of Preact 10.26.5 through 10.28.1 should upgrade to the appropriate patched version (10.26.10, 10.27.3, or 10.28.2) as soon as possible, and review their applications for proper input validation and sanitization practices.

## References
- https://github.com/preactjs/preact/security/advisories/GHSA-36hm-qxxp-pg3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-22028
- https://github.com/preactjs/preact
