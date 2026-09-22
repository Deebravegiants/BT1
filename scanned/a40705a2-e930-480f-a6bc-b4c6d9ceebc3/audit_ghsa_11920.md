# [H] OpenClaw: Plivo V2 verified replay identity drifts on query-only variants

## Summary
Severity: High
Advisory: GHSA-cg6c-q2hx-69h7
CVE: CVE-2026-35618
CWE: CWE-294
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-cg6c-q2hx-69h7
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.23

## Details
## Summary
Before `v2026.3.23`, the Plivo V2 verification path treated query-only variants of the same signed request as fresh verified work. Plivo V2 signatures authenticate `baseUrl + nonce`, but the replay key was derived from the full verification URL including the query string, so unsigned query-only changes minted a new `verifiedRequestKey`.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `< 2026.3.23`
- Fixed: `>= 2026.3.23`
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Root Cause
The vulnerable logic lived in `extensions/voice-call/src/webhook-security.ts`. V2 signature validation already canonicalized to the base URL without query parameters, but the replay key used the full `verificationUrl`, letting query-only variants bypass replay identity stability.

## Fix Commit(s)
- `b0ce53a79cf63834660270513e26d921899b4e5b` — `fix(voice-call): stabilize plivo v2 replay keys`

## Release Status
The fix commit is contained in released tags `v2026.3.23` and `v2026.3.23-2`. The latest shipped tag and npm release both include the fix.

## Code-Level Confirmation
- `extensions/voice-call/src/webhook-security.ts` now derives the V2 replay key with `createPlivoV2ReplayKey(...)`, which hashes `getBaseUrlNoQuery(url)` plus the nonce.
- `extensions/voice-call/src/webhook-security.test.ts` contains the regression test `treats query-only V2 variants as the same verified request`.

Thanks @smaeljaish771 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cg6c-q2hx-69h7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35618
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/b0ce53a79cf63834660270513e26d921899b4e5b
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-replay-identity-drift-via-query-only-variants-in-plivo-v2-verification
