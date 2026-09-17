# [M] Flowise: Weak Default Token Hash Secret

## Summary
Severity: Medium
Advisory: GHSA-m7mq-85xj-9x33
CVE: CVE-2026-56269
CWE: CWE-798
Ecosystem: npm
CVSS: CVSS:3.0/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-m7mq-85xj-9x33
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0

## Details
**Detection Method:** Kolega.dev Deep Code Scan

| Attribute | Value |
|---|---|
| Location | packages/server/src/enterprise/utils/tempTokenUtils.ts:31-34 |
| Practical Exploitability | Medium |
| Developer Approver | faizan@kolega.ai |

### Description
The encryption key for token encryption has a weak default value 'Secre$t' when TOKEN_HASH_SECRET environment variable is not set.

### Affected Code
```
const key = crypto
    .createHash('sha256')
    .update(process.env.TOKEN_HASH_SECRET || 'Secre$t')
    .digest()
```

### Evidence
The default value 'Secre$t' is hardcoded in the source code and is cryptographically weak. This key is used to encrypt user IDs and workspace IDs in JWT tokens.

### Impact
Token forgery - attackers can decrypt and manipulate encrypted token metadata, potentially changing user IDs or workspace IDs to escalate privileges or access unauthorized data.

### Recommendation
Require TOKEN_HASH_SECRET to be set as a strong random value in environment variables. Throw an error on startup if not configured. Use a minimum of 32 bytes of entropy.

### Notes
The TOKEN_HASH_SECRET has a weak hardcoded default 'Secre$t' (lines 31-34 and 50-53). This secret is used to derive an AES-256-CBC encryption key for encrypting sensitive metadata (user ID and workspace ID) embedded in JWT tokens via encryptToken() called at line 394 of passport/index.ts. If TOKEN_HASH_SECRET is not configured, an attacker knowing the default can decrypt the 'meta' field in JWTs to extract user IDs and workspace IDs. While this alone doesn't grant access (the JWT signature is separate), it leaks internal identifiers that could aid other attacks. The .env.example shows '# TOKEN_HASH_SECRET='popcorn'' - another weak value, and it's commented out suggesting it's optional. The application should require this secret to be explicitly set with a strong random value.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-m7mq-85xj-9x33
- https://nvd.nist.gov/vuln/detail/CVE-2026-56269
- https://github.com/FlowiseAI/Flowise
- https://www.vulncheck.com/advisories/flowise-weak-default-token-hash-secret-in-jwt-token-encryption
