# [M] ws: Uninitialized memory disclosure

## Summary
Severity: Medium
Advisory: GHSA-58qx-3vcg-4xpx
CVE: CVE-2026-45736
CWE: CWE-908
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-58qx-3vcg-4xpx
Type: github-advisory

## Affected
- npm: `ws` — affected >=8.0.0 <8.20.1

## Details
### Impact

The `websocket.close()` implementation is vulnerable to uninitialized memory disclosure when a `TypedArray` is passed as the reason argument.

### Proof of concept

```js
import { deepStrictEqual } from 'node:assert';
import { WebSocket, WebSocketServer } from 'ws';

const wss = new WebSocketServer(
  { port: 0, skipUTF8Validation: true },
  function () {
    const { port } = wss.address();
    const ws = new WebSocket(`ws://localhost:${port}`, {
      skipUTF8Validation: true
    });

    ws.on('close', function (code, reason) {
      deepStrictEqual(reason, Buffer.alloc(80));
    });
  }
);

wss.on('connection', function (ws) {
  ws.close(1000, new Float32Array(20));
});
```

### Patches

The vulnerability was fixed in ws@8.20.1 (https://github.com/websockets/ws/commit/c0327ec15a54d701eb6ccefaa8bef328cfc03086).

### Credits

Credit for the private and responsible disclosure of this issue goes to [Nikita Skovoroda](https://github.com/ChALkeR).

### Remarks

Although the calculated CVSS severity is medium, the actual severity is believed to be low, as the flaw is only exploitable through misuse that is unlikely in practice.

### Resources

- https://github.com/advisories/GHSA-58qx-3vcg-4xpx
- https://www.cve.org/CVERecord?id=CVE-2026-45736

## References
- https://github.com/websockets/ws/security/advisories/GHSA-58qx-3vcg-4xpx
- https://nvd.nist.gov/vuln/detail/CVE-2026-45736
- https://github.com/websockets/ws/commit/c0327ec15a54d701eb6ccefaa8bef328cfc03086
- https://github.com/websockets/ws
