# [H] Uncaught Exception in engine.io

## Summary
Severity: High
Advisory: GHSA-273r-mgr4-v34f
CVE: CVE-2022-21676
CWE: CWE-754, CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-273r-mgr4-v34f
Type: github-advisory

## Affected
- npm: `engine.io` — affected >=4.0.0 <4.1.2
- npm: `engine.io` — affected >=5.0.0 <5.2.1
- npm: `engine.io` — affected >=6.0.0 <6.1.1

## Details
### Impact

A specially crafted HTTP request can trigger an uncaught exception on the Engine.IO server, thus killing the Node.js process.

> RangeError: Invalid WebSocket frame: RSV2 and RSV3 must be clear
>   at Receiver.getInfo (/.../node_modules/ws/lib/receiver.js:176:14)
>   at Receiver.startLoop (/.../node_modules/ws/lib/receiver.js:136:22)
>   at Receiver._write (/.../node_modules/ws/lib/receiver.js:83:10)
>   at writeOrBuffer (internal/streams/writable.js:358:12)

This impacts all the users of the [`engine.io`](https://www.npmjs.com/package/engine.io) package starting from version `4.0.0`, including those who uses depending packages like [`socket.io`](https://www.npmjs.com/package/socket.io).

### Patches

A fix has been released for each major branch:

| Version range | Fixed version |
| --- | --- |
| `engine.io@4.x.x` | `4.1.2` |
| `engine.io@5.x.x` | `5.2.1` |
| `engine.io@6.x.x` | `6.1.1` |

Previous versions (`< 4.0.0`) are not impacted.

For `socket.io` users:

| Version range | `engine.io` version | Needs minor update? |
| --- | --- | --- |
| `socket.io@4.4.x` | `~6.1.0` | -
| `socket.io@4.3.x` | `~6.0.0` | Please upgrade to `socket.io@4.4.x`
| `socket.io@4.2.x` | `~5.2.0` | -
| `socket.io@4.1.x` | `~5.1.1` | Please upgrade to `socket.io@4.4.x`
| `socket.io@4.0.x` | `~5.0.0` | Please upgrade to `socket.io@4.4.x`
| `socket.io@3.1.x` | `~4.1.0` | -
| `socket.io@3.0.x` | `~4.0.0` | Please upgrade to `socket.io@3.1.x` or `socket.io@4.4.x` (see [here](https://socket.io/docs/v4/migrating-from-3-x-to-4-0/))

In most cases, running `npm audit fix` should be sufficient. You can also use  `npm update engine.io --depth=9999`.

### Workarounds

There is no known workaround except upgrading to a safe version.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [`engine.io`](https://github.com/socketio/engine.io)

Thanks to Marcus Wejderot from Mevisio for the responsible disclosure.

## References
- https://github.com/socketio/engine.io/security/advisories/GHSA-273r-mgr4-v34f
- https://nvd.nist.gov/vuln/detail/CVE-2022-21676
- https://github.com/socketio/engine.io/commit/66f889fc1d966bf5bfa0de1939069153643874ab
- https://github.com/socketio/engine.io/commit/a70800d7e96da32f6e6622804ef659ebc58659db
- https://github.com/socketio/engine.io/commit/c0e194d44933bd83bf9a4b126fca68ba7bf5098c
- https://github.com/socketio/engine.io
- https://github.com/socketio/engine.io/releases/tag/4.1.2
- https://github.com/socketio/engine.io/releases/tag/5.2.1
- https://github.com/socketio/engine.io/releases/tag/6.1.1
- https://security.netapp.com/advisory/ntap-20220209-0002
