# [M] Uncaught exception in engine.io

## Summary
Severity: Medium
Advisory: GHSA-r7qp-cfhv-p84w
CVE: CVE-2022-41940
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-r7qp-cfhv-p84w
Type: github-advisory

## Affected
- npm: `engine.io` — affected >=0 <3.6.1
- npm: `engine.io` — affected >=4.0.0 <6.2.1

## Details
### Impact

A specially crafted HTTP request can trigger an uncaught exception on the Engine.IO server, thus killing the Node.js process.

```
events.js:292
      throw er; // Unhandled 'error' event
      ^

Error: read ECONNRESET
    at TCP.onStreamRead (internal/stream_base_commons.js:209:20)
Emitted 'error' event on Socket instance at:
    at emitErrorNT (internal/streams/destroy.js:106:8)
    at emitErrorCloseNT (internal/streams/destroy.js:74:3)
    at processTicksAndRejections (internal/process/task_queues.js:80:21) {
  errno: -104,
  code: 'ECONNRESET',
  syscall: 'read'
}
```

This impacts all the users of the [`engine.io`](https://www.npmjs.com/package/engine.io) package, including those who uses depending packages like [`socket.io`](https://www.npmjs.com/package/socket.io).

### Patches

A fix has been released today (2022/11/20):

| Version range     | Fixed version |
|-------------------|---------------|
| `engine.io@3.x.y` | `3.6.1`       |
| `engine.io@6.x.y` | `6.2.1`       |

For `socket.io` users:

| Version range               | `engine.io` version | Needs minor update?                                                                                    |
|-----------------------------|---------------------|--------------------------------------------------------------------------------------------------------|
| `socket.io@4.5.x`           | `~6.2.0`            | `npm audit fix` should be sufficient                                                                   |
| `socket.io@4.4.x`           | `~6.1.0`            | Please upgrade to `socket.io@4.5.x`                                                                    |
| `socket.io@4.3.x`           | `~6.0.0`            | Please upgrade to `socket.io@4.5.x`                                                                    |
| `socket.io@4.2.x`           | `~5.2.0`            | Please upgrade to `socket.io@4.5.x`                                                                    |
| `socket.io@4.1.x`           | `~5.1.1`            | Please upgrade to `socket.io@4.5.x`                                                                    |
| `socket.io@4.0.x`           | `~5.0.0`            | Please upgrade to `socket.io@4.5.x`                                                                    |
| `socket.io@3.1.x`           | `~4.1.0`            | Please upgrade to `socket.io@4.5.x` (see [here](https://socket.io/docs/v4/migrating-from-3-x-to-4-0/)) |
| `socket.io@3.0.x`           | `~4.0.0`            | Please upgrade to `socket.io@4.5.x` (see [here](https://socket.io/docs/v4/migrating-from-3-x-to-4-0/)) |
| `socket.io@2.5.0`           | `~3.6.0`            | `npm audit fix` should be sufficient                                                                   |
| `socket.io@2.4.x` and below | `~3.5.0`            | Please upgrade to `socket.io@2.5.0`                                                                    |

### Workarounds

There is no known workaround except upgrading to a safe version.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [`engine.io`](https://github.com/socketio/engine.io)

Thanks to [Jonathan Neve](https://github.com/jonathanneve) for the responsible disclosure.

## References
- https://github.com/socketio/engine.io/security/advisories/GHSA-r7qp-cfhv-p84w
- https://nvd.nist.gov/vuln/detail/CVE-2022-41940
- https://github.com/socketio/engine.io/commit/425e833ab13373edf1dd5a0706f07100db14e3c6
- https://github.com/socketio/engine.io/commit/83c4071af871fc188298d7d591e95670bf9f9085
- https://github.com/socketio/engine.io
