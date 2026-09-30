# [M] fast-jwt: Stateful RegExp (/g or /y) causes non-deterministic allowed-claim validation (logical DoS)

## Summary
Severity: Medium
Advisory: GHSA-3j8v-cgw4-2g6q
CVE: CVE-2026-35040
CWE: CWE-440, CWE-697
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-3j8v-cgw4-2g6q
Type: github-advisory

## Affected
- npm: `fast-jwt` — affected >=0 <6.2.1

## Details
## Impact

Using certain modifiers on RegExp objects in the allowedAud, allowedIss, allowedSub, allowedJti, or allowedNonce options in verify functions can cause certain unintended behaviours. This is because some modifiers are stateful and will cause failures in every second verification attempt regardless of the validity of the token provided.

Such modifiers are:
- /g : Global matching
- /y : Sticky matching

This does NOT allow invalid tokens to be accepted, only for valid tokens to be improperly rejected in some configurations. Instead it causes **50% of valid authentication requests to fail** in an alternating pattern, leading to:
  - Intermittent user authentication failures
  - Potential retry storms in applications
  - Operational monitoring alerts

## Affected Configurations

### This vulnerability ONLY affects applications that:

- Use RegExp objects (not strings) in the allowedAud, allowedIss, allowedSub, allowedJti, or allowedNonce options
- Use stateful RegExp modifiers such a /g or /y

Example: allowedAud: /abc/g ← IMPACTED
Example: allowedAud: "/abc/" ← SAFE

### Not Affected

- Applications using string patterns for audience validation (most common)
- Applications using RegExp patterns without stateful modifiers

### Assessment Guide
To determine if you're affected:

Check if  allowedAud, allowedIss, allowedSub, allowedJti, or allowedNonce options use RegExp objects (/pattern/ or new RegExp())
If yes, review the pattern for stateful modifiers like /g, /y
If no RegExp usage or no stateful modifiers, you are NOT affected

## Mitigation Options
While a fix will be coming in the next version of the package you can take steps to mitigate the issue immediately by removing any such modifiers (/g, /y) from the regex.

---

Summary

fast-jwt accepts RegExp for allowedAud, allowedIss, allowedSub, allowedJti, and allowedNonce.

If the provided regular expression uses the g (global) or y (sticky) flag, verification becomes non-deterministic: the same valid token alternates between acceptance and rejection across successive calls.

This occurs because RegExp.prototype.test() is stateful when g/y is set (it mutates lastIndex), and fast-jwt reuses the same RegExp object without resetting lastIndex.


Affected component

src/verifier.js

ensureStringClaimMatcher() returns the RegExp object directly.

validateClaimValues() performs repeated a.test(v) calls without resetting lastIndex.


Impact

Logical denial-of-service / authentication flapping.

A valid signed JWT can be intermittently rejected.

Causes unpredictable authentication outcomes across repeated verification calls.

Can trigger retry storms and cascading failures in API gateways and authentication middleware.

Affects any deployment that configures allowed* using RegExp and includes g or y flags.


Root cause

validateClaimValues() uses: allowed.some(a => a.test(v))


When `a` is a RegExp with g or y, `a.test()` mutates `a.lastIndex`.

Subsequent calls against the same input can return different results.


Proof of concept

Environment

- fast-jwt: 6.1.0 (repo HEAD)
- Node.js: v24.13.1

PoC
const { createSigner, createVerifier } = require('fast-jwt')

const sign = createSigner({ key: 'secret' })
const token = sign({ aud: 'admin', iss: 'issuer' })

function run(name, opts) {
const verify = createVerifier({ key: 'secret', ...opts })
console.log('\n==', name)
for (let i = 0; i < 8; i++) {
try { verify(token); console.log(i, 'PASS') }
catch (e) { console.log(i, 'FAIL', e.code || e.message) }
}
}

run('allowedAud global regex', { allowedAud: /^admin$/g })
run('allowedIss global regex', { allowedIss: /^issuer$/g })
run('control (non-global regex)', { allowedAud: /^admin$/ })



Observed behavior

- allowedAud with `/g` alternates PASS/FAIL across calls
- allowedIss with `/g` alternates PASS/FAIL across calls
- control regex (no g/y) is deterministic and always PASS


Expected behavior

Validation must be deterministic.

The same token under the same verifier configuration must always yield the same decision.


Suggested fix (minimal and safe)

Wrap RegExp matchers inside ensureStringClaimMatcher() to reset lastIndex before calling test():
if (r instanceof RegExp) {
return { test: v => { r.lastIndex = 0; return r.test(v) } }
}


This preserves semantics for non-global regexes, makes g/y deterministic, and avoids changes in the rest of the verifier logic.


Security classification

Logical DoS / authentication reliability failure.

This can be weaponized to produce production outages via retry storms and auth instability.


Why this is not “misuse”

- The library explicitly accepts RegExp for allowed* claim validation.
- The behavior difference is caused by internal state mutation of RegExp.test().
- The same token, same verifier config, same runtime yields different outcomes.
- Security decisions must be deterministic; non-determinism at the verification layer is a correctness flaw.
- Consumers cannot reliably defend against this unless the library normalizes matcher state.


Notes

- Affects allowedAud, allowedIss, allowedSub, allowedJti, allowedNonce equally (shared matcher logic).
- Independent from the previously reported ReDoS; this is a determinism and correctness failure that can still produce production DoS effects.


PoC Code:
'use strict'

/**
 * PoC: Stateful RegExp flags (g/y) cause non-deterministic allowed-claim validation
 * fast-jwt reuses the same RegExp object; RegExp.test() mutates lastIndex when g/y is set.
 *
 * This script prints a human-readable log AND writes evidence to JSON.
 *
 * Usage:
 *   node poc_regex_state_evidence.js
 */

const fs = require('node:fs')
const path = require('node:path')
const { createSigner, createVerifier } = require('fast-jwt')

const OUT_JSON = path.join(process.cwd(), 'evidence-regex-stateful-fastjwt.json')
const OUT_LOG  = path.join(process.cwd(), 'evidence-regex-stateful-fastjwt.log')

// Make a stable, valid token
const sign = createSigner({ key: 'secret' })
const token = sign({
  aud: 'admin',
  iss: 'issuer',
  sub: 'subject',
  jti: 'id-123',
  nonce: 'nonce-xyz'
})

function runCase(name, verifierOpts, iterations = 12) {
  const verify = createVerifier({ key: 'secret', ...verifierOpts })

  const results = []
  for (let i = 0; i < iterations; i++) {
    try {
      verify(token)
      results.push({ i, ok: true })
    } catch (e) {
      results.push({ i, ok: false, code: e.code || null, message: e.message || String(e) })
    }
  }

  return results
}

function summarize(results) {
  const seq = results.map(r => (r.ok ? 'PASS' : 'FAIL')).join(' ')
  const pass = results.filter(r => r.ok).length
  const fail = results.length - pass
  return { pass, fail, seq }
}

function printCase(name, opts, results) {
  const s = summarize(results)
  const lines = []
  lines.push(`== ${name}`)
  lines.push(`opts: ${JSON.stringify(opts)}`)
  lines.push(`PASS=${s.pass} FAIL=${s.fail}`)
  lines.push(`sequence: ${s.seq}`)
  lines.push('')
  return lines.join('\n')
}

function main() {
  const meta = {
    poc: 'stateful-regexp-allowed-claims',
    package: 'fast-jwt',
    node: process.version,
    timestamp: new Date().toISOString(),
    note: 'RegExp.test is stateful when g/y flags are set; lastIndex mutation causes alternating PASS/FAIL.'
  }

  // Cases: g/y should flap, control should be stable
  const cases = [
    {
      name: 'allowedAud with global RegExp /g (expected: flapping)',
      opts: { allowedAud: /^admin$/g }
    },
    {
      name: 'allowedAud with sticky RegExp /y (expected: flapping)',
      opts: { allowedAud: /^admin$/y }
    },
    {
      name: 'allowedIss with global RegExp /g (expected: flapping)',
      opts: { allowedIss: /^issuer$/g }
    },
    {
      name: 'allowedSub with global RegExp /g (expected: flapping)',
      opts: { allowedSub: /^subject$/g }
    },
    {
      name: 'allowedJti with global RegExp /g (expected: flapping)',
      opts: { allowedJti: /^id-123$/g }
    },
    {
      name: 'allowedNonce with global RegExp /g (expected: flapping)',
      opts: { allowedNonce: /^nonce-xyz$/g }
    },
    {
      name: 'CONTROL: allowedAud with non-global RegExp (expected: stable PASS)',
      opts: { allowedAud: /^admin$/ }
    }
  ]

  const evidence = {
    meta,
    token: {
      alg: 'HS256 (autodetected by fast-jwt)',
      signed: true,
      jwt: token
    },
    cases: []
  }

  let log = ''
  for (const c of cases) {
    const results = runCase(c.name, c.opts, 12)
    const s = summarize(results)

    evidence.cases.push({
      name: c.name,
      opts: c.opts,
      iterations: results.length,
      pass: s.pass,
      fail: s.fail,
      sequence: s.seq,
      results
    })

    log += printCase(c.name, c.opts, results)
  }

  fs.writeFileSync(OUT_JSON, JSON.stringify(evidence, null, 2))
  fs.writeFileSync(OUT_LOG, log)

  console.log(log)
  console.log(`[+] Wrote JSON evidence: ${OUT_JSON}`)
  console.log(`[+] Wrote LOG evidence : ${OUT_LOG}`)
}

main()


Output:
PS C:\Users\Franciny Rojas\Desktop\crypto-research\fast-jwt> node .\poc_regex_state_evidence.js
== allowedAud with global RegExp /g (expected: flapping)
opts: {"allowedAud":{}}
PASS=6 FAIL=6
sequence: PASS FAIL PASS FAIL PASS FAIL PASS FAIL PASS FAIL PASS FAIL
== allowedAud with sticky RegExp /y (expected: flapping)
opts: {"allowedAud":{}}
PASS=6 FAIL=6
sequence: PASS FAIL PASS FAIL PASS FAIL PASS FAIL PASS FAIL PASS FAIL
== allowedIss with global RegExp /g (expected: flapping)
opts: {"allowedIss":{}}
PASS=6 FAIL=6
sequence: PASS FAIL PASS FAIL PASS FAIL PASS FAIL PASS FAIL PASS FAIL
== allowedSub with global RegExp /g (expected: flapping)
opts: {"allowedSub":{}}
PASS=6 FAIL=6
sequence: PASS FAIL PASS FAIL PASS FAIL PASS FAIL PASS FAIL PASS FAIL
== allowedJti with global RegExp /g (expected: flapping)
opts: {"allowedJti":{}}
PASS=6 FAIL=6
sequence: PASS FAIL PASS FAIL PASS FAIL PASS FAIL PASS FAIL PASS FAIL
== allowedNonce with global RegExp /g (expected: flapping)
opts: {"allowedNonce":{}}
PASS=6 FAIL=6
sequence: PASS FAIL PASS FAIL PASS FAIL PASS FAIL PASS FAIL PASS FAIL
== CONTROL: allowedAud with non-global RegExp (expected: stable PASS)
opts: {"allowedAud":{}}
PASS=12 FAIL=0
sequence: PASS PASS PASS PASS PASS PASS PASS PASS PASS PASS PASS PASS

[+] Wrote JSON evidence: C:\Users\Franciny Rojas\Desktop\crypto-research\fast-jwt\evidence-regex-stateful-fastjwt.json
[+] Wrote LOG evidence : C:\Users\Franciny Rojas\Desktop\crypto-research\fast-jwt\evidence-regex-stateful-fastjwt.log
PS C:\Users\Franciny Rojas\Desktop\crypto-research\fast-jwt>

## References
- https://github.com/nearform/fast-jwt/security/advisories/GHSA-3j8v-cgw4-2g6q
- https://nvd.nist.gov/vuln/detail/CVE-2026-35040
- https://github.com/nearform/fast-jwt/pull/593
- https://github.com/nearform/fast-jwt/commit/18d25904e4617e8753526d1b3ab5a2cccdea726a
- https://github.com/nearform/fast-jwt
- https://github.com/nearform/fast-jwt/releases/tag/v6.2.1
