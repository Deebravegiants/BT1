# [H] Flowise: Unauthenticated TTS endpoint accepts arbitrary credential IDs — enables API credit abuse via stored credentials

## Summary
Severity: High
Advisory: GHSA-5fw2-mwhh-9947
CVE: CVE-2026-41279
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-5fw2-mwhh-9947
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0

## Details
### Summary

The text-to-speech generation endpoint (`POST /api/v1/text-to-speech/generate`) is whitelisted (no auth) and accepts a `credentialId` directly in the request body. When called without a `chatflowId`, the endpoint uses the provided `credentialId` to decrypt the stored credential (e.g., OpenAI or ElevenLabs API key) and generate speech.

### Root Cause

```typescript
// packages/server/src/controllers/text-to-speech/index.ts:58-64
} else {
    // Use TTS config from request body
    provider = bodyProvider
    credentialId = bodyCredentialId  // ← attacker-controlled credential ID
    voice = bodyVoice
    model = bodyModel
}
```

### Docker Validation

`POST /api/v1/text-to-speech/generate` with arbitrary `credentialId` in body: endpoint processes request, sends SSE `tts_start` event, only fails when credential doesn't exist — proves code path runs without authentication.

### Impact

- Use victim's API keys (OpenAI, ElevenLabs, Azure, Google) without authorization
- Burn API credits on the victim's account
- Generate unlimited speech content at victim's expense
- Combined with credential ID leak from Finding 2, this is trivially exploitable

### Suggested Fix

Remove the TTS endpoint from `WHITELIST_URLS` or validate that the credential belongs to the chatflow being used:

```typescript
// Only allow credentialId when it matches the chatflow's TTS configuration
if (!chatflowId) {
    return res.status(401).json({ message: 'Authentication required' })
}
```

---

## References

- `packages/server/src/controllers/text-to-speech/index.ts` lines 10-162
- `packages/server/src/utils/constants.ts` line 41 (whitelist entry)

## Credits
- Shinobi Security - https://github.com/shinobisecurity

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-5fw2-mwhh-9947
- https://nvd.nist.gov/vuln/detail/CVE-2026-41279
- https://github.com/FlowiseAI/Flowise
