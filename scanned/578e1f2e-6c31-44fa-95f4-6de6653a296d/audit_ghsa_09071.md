# [M] Flowise: Hardcoded CORS wildcard on TTS endpoint enables cross-origin credential abuse from any webpage

## Summary
Severity: Medium
Advisory: GHSA-m837-xvxr-vqwg
CWE: CWE-942
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-m837-xvxr-vqwg
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.2

## Details
### Summary

The TTS generation endpoint sets `Access-Control-Allow-Origin: *` as a hardcoded response header, independent of the server's CORS configuration. This enables any webpage to make cross-origin requests to generate speech using stored credentials.

### Root Cause

```typescript
// packages/server/src/controllers/text-to-speech/index.ts:83
res.setHeader('Access-Control-Allow-Origin', '*')
res.setHeader('Access-Control-Allow-Headers', 'Cache-Control')
```

### Impact

- Cross-origin credential abuse — any webpage can trigger TTS using stored credentials
- Bypasses the server's CORS policy (`getCorsOptions()`) which is otherwise restrictive by default
- Combined with Finding 3 (TTS credential abuse), enables drive-by credential abuse via malicious webpages

### Suggested Fix

Remove the hardcoded CORS wildcard and let the server's CORS middleware handle the headers:

```typescript
// Remove these lines:
// res.setHeader('Access-Control-Allow-Origin', '*')
// res.setHeader('Access-Control-Allow-Headers', 'Cache-Control')
```

---

## References

- `packages/server/src/controllers/text-to-speech/index.ts` line 83

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-m837-xvxr-vqwg
- https://github.com/FlowiseAI/Flowise
