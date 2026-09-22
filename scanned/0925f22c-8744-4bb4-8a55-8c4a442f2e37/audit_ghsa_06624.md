# [H] sigstore's `certificateOIDs` verification constraints are silently dropped and never enforced

## Summary
Severity: High
Advisory: GHSA-52v5-jr5w-gjxr
CVE: CVE-2026-48815
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-52v5-jr5w-gjxr
Type: github-advisory

## Affected
- npm: `sigstore` — affected >=0 <4.1.1

## Details
### Summary

The documented `certificateOIDs` option in `sigstore.verify()` is accepted by the public API but discarded before verification, so required certificate extension OIDs are never checked.

### Details

The public verify options include `certificateOIDs` and the documentation says those OID/value pairs “must be present in the certificate’s extension list.” The policy-construction path used by `sigstore.verify()` and `createVerifier()` only copies the SAN and issuer settings into the verification policy and completely ignores `certificateOIDs`.

As a result, callers can believe they are constraining verification to certificates carrying specific Fulcio or workload-identifying OIDs, while the actual verifier never receives those constraints. Any bundle that satisfies the remaining checks is accepted even if the required OID extensions are absent or mismatched.

This is reachable from supported usage through the documented `certificateOIDs` verify option.

### PoC

```javascript
const { createVerificationPolicy } = require("sigstore/dist/config");

const policy = createVerificationPolicy({
  certificateIssuer: "https://issuer.example",
  certificateIdentityEmail: "victim@example.com",
  certificateOIDs: {
    "1.2.3.4": "required-value",
  },
});

console.log("certificateOIDs" in policy, JSON.stringify(policy));
// false {"subjectAlternativeName":"victim@example.com","extensions":{"issuer":"https://issuer.example"}}
```

### Impact

Applications that rely on `certificateOIDs` to restrict which certificates may sign artifacts receive no such protection. Unauthorized certificates that should be rejected on extension policy can be accepted as long as they satisfy the remaining verification checks.

## References
- https://github.com/sigstore/sigstore-js/security/advisories/GHSA-52v5-jr5w-gjxr
- https://github.com/sigstore/sigstore-js
