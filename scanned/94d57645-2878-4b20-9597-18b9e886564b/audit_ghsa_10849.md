# [H] Prototype Pollution via parse() in NodeJS flatted

## Summary
Severity: High
Advisory: GHSA-rf6f-7fwh-wjgh
CVE: CVE-2026-33228
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-rf6f-7fwh-wjgh
Type: github-advisory

## Affected
- npm: `flatted` — affected >=0 <3.4.2

## Details
---
  **Summary**

  The parse() function in flatted can use attacker-controlled string values from the parsed JSON as direct array index
  keys, without validating that they are numeric. Since the internal input buffer is a JavaScript Array, accessing it
  with the key "\_\_proto\_\_" returns Array.prototype via the inherited getter. This object is then treated as a legitimate
   parsed value and assigned as a property of the output object, effectively leaking a live reference to Array.prototype
   to the consumer. Any code that subsequently writes to that property will pollute the global prototype.

  ---
  **Root Cause**

  File: esm/index.js:29 (identical in cjs/index.js)
```
  const resolver = (input, lazy, parsed, $) => output => {
    for (let ke = keys(output), {length} = ke, y = 0; y < length; y++) {
      const k = ke[y];
      const value = output[k];    
      if (value instanceof Primitive) {
        const tmp = input[value];      // Bug is here
```

No validation that value is a safe numeric index input is built as a plain Array. JavaScript's property lookup on arrays traverses the prototype chain for non-numeric  keys. The key "\_\_proto\_\_" resolves to Array.prototype, which:

  - has type "object" → passes the typeof tmp === object guard at line 30
  - is not in the parsed Set yet → passes the !parsed.has(tmp) guard.
  - The reference to Array.prototype is then enqueued in lazy and later unconditionally assigned to the output object.
  ---
  **Replication Steps**
```
  const Flatted = require('flatted'); 
  const parsed = Flatted.parse('[{"x":"__proto__"}]');
  parsed.x.polluted = 'pwned';
  console.log([].polluted);  // Returns true
``` 
 ---
  **Impact**
 An attacker can supply a crafted flatted string to parse() that causes the returned object to hold a live reference to Array.prototype, enabling any downstream code that writes to that property to pollute the global prototype chain, potentially causing denial of service or code execution.

  **Recommended solution**
 Validate that the index string represents an integer within the bounds of input before accessing it:

  // Before (vulnerable)
  const tmp = input[value];

  // After (safe)
  const idx = +value;  // coerce boxed String → number
  const tmp = (Number.isInteger(idx) && idx >= 0 && idx < input.length)
    ? input[idx]
    : undefined;

## References
- https://github.com/WebReflection/flatted/security/advisories/GHSA-rf6f-7fwh-wjgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33228
- https://github.com/WebReflection/flatted/commit/885ddcc33cf9657caf38c57c7be45ae1c5272802
- https://github.com/WebReflection/flatted
- https://github.com/WebReflection/flatted/releases/tag/v3.4.2
