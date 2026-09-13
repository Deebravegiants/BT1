# [H] FlowiseAI Vulnerable to Credential Data Leak

## Summary
Severity: High
Advisory: GHSA-7g73-99r4-m4mj
CVE: CVE-2026-46443
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-7g73-99r4-m4mj
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.2

## Details
**Severity**: HIGH (CVSS ~7.5)
**Type**: CWE-200 (Exposure of Sensitive Information)
**File**: `packages/server/src/services/credentials/index.ts:62-71`

**Description**: When credentials are fetched with a `credentialName` filter parameter, the `encryptedData` field is NOT stripped from the response. The code properly omits `encryptedData` when NO filter is used (line 102) but fails to do so when a filter IS used (lines 62-63, 70-71).
Credential Data Leak
**Evidence**:
```typescript
// Lines 62-63: WITH filter - encryptedData LEAKED
const credentials = await appServer.AppDataSource.getRepository(Credential).findBy(searchOptions)
dbResponse.push(...credentials)  // encryptedData NOT removed!

// Lines 100-102: WITHOUT filter - encryptedData properly omitted
for (const credential of credentials) {
    dbResponse.push(omit(credential, ['encryptedData']))  // Correctly omitted
}
```

**Impact**: Authenticated users can extract encrypted credential data (API keys, passwords, tokens for services like OpenAI, AWS, etc.). Combined with access to the encryption key file (`~/.flowise/encryption.key` written with default permissions), this enables full credential theft.

**Reproduction**:
```bash
curl https://TARGET/api/v1/credentials?credentialName=openAIApi \
  -H "Authorization: Bearer API_KEY"
# Response includes encryptedData field with AES-encrypted credentials
```

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-7g73-99r4-m4mj
- https://nvd.nist.gov/vuln/detail/CVE-2026-46443
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.1.2
