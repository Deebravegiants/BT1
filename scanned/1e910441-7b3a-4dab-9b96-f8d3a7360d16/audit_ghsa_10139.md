# [H] fast-jwt accepts unknown `crit` header extensions (RFC 7515 violation)

## Summary
Severity: High
Advisory: GHSA-hm7r-c7qw-ghp6
CVE: CVE-2026-35042
CWE: CWE-345, CWE-636
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-hm7r-c7qw-ghp6
Type: github-advisory

## Affected
- npm: `fast-jwt` — affected >=0

## Details
## Summary

`fast-jwt` does not validate the `crit` (Critical) Header Parameter defined in RFC 7515 §4.1.11. When a JWS token contains a `crit` array listing extensions that `fast-jwt` does not understand, the library accepts the token instead of rejecting it. This violates the **MUST** requirement in the RFC.

---

## RFC Requirement

RFC 7515 §4.1.11:

> If any of the listed extension Header Parameters are **not understood
> and supported** by the recipient, then the **JWS is invalid**.

---

## Proof of Concept

```javascript
const { createSigner, createVerifier } = require("fast-jwt"); // v3.3.3

const signer = createSigner({ key: "secret", algorithm: "HS256" });
const token = signer({
  sub: "attacker",
  role: "admin",
  header: { crit: ["x-custom-policy"], "x-custom-policy": "require-mfa" },
});

// Should REJECT — x-custom-policy is not understood
const verifier = createVerifier({ key: "secret", algorithms: ["HS256"] });
try {
  const result = verifier(token);
  console.log("ACCEPTED:", result);
  // Output: ACCEPTED: { sub: 'attacker', role: 'admin' }
} catch (e) {
  console.log("REJECTED:", e.message);
}
```

**Expected:** Error — unsupported critical extension
**Actual:** Token accepted.

### Comparison

```javascript
// jose (panva) v4+ — correctly rejects
const jose = require("jose");
await jose.jwtVerify(token, new TextEncoder().encode("secret"));
// throws: Extension Header Parameter "x-custom-policy" is not recognized
```

---

## Impact

- **Split-brain verification** in mixed-library environments
- **Security policy bypass** when `crit` carries enforcement semantics
- **Token binding bypass** (RFC 7800 `cnf` confirmation)
- See CVE-2025-59420 for full impact analysis

---

## Suggested Fix

In `src/verifier.js`, add crit validation after header decoding:

```javascript
const SUPPORTED_CRIT = new Set(["b64"]);

function validateCrit(header) {
  if (!header.crit) return;
  if (!Array.isArray(header.crit) || header.crit.length === 0)
    throw new Error("crit must be a non-empty array");
  for (const ext of header.crit) {
    if (!SUPPORTED_CRIT.has(ext))
      throw new Error(`Unsupported critical extension: ${ext}`);
    if (!(ext in header))
      throw new Error(`Critical extension ${ext} not present in header`);
  }
}
```

## References
- https://github.com/nearform/fast-jwt/security/advisories/GHSA-hm7r-c7qw-ghp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-35042
- https://github.com/advisories/GHSA-9ggr-2464-2j32
- https://github.com/nearform/fast-jwt
- https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.11
