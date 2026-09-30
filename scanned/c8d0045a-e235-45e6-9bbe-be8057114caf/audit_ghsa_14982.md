# [M] socket.io has an unhandled 'error' event

## Summary
Severity: Medium
Advisory: GHSA-25hc-qcg6-38wj
CVE: CVE-2024-38355
CWE: CWE-20, CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-06-19
Source: https://github.com/advisories/GHSA-25hc-qcg6-38wj
Type: github-advisory

## Affected
- npm: `socket.io` — affected >=0 <2.5.1
- npm: `socket.io` — affected >=3.0.0 <4.6.2

## Details
### Impact

A specially crafted Socket.IO packet can trigger an uncaught exception on the Socket.IO server, thus killing the Node.js process.

```
node:events:502
    throw err; // Unhandled 'error' event
    ^

Error [ERR_UNHANDLED_ERROR]: Unhandled error. (undefined)
    at new NodeError (node:internal/errors:405:5)
    at Socket.emit (node:events:500:17)
    at /myapp/node_modules/socket.io/lib/socket.js:531:14
    at process.processTicksAndRejections (node:internal/process/task_queues:77:11) {
  code: 'ERR_UNHANDLED_ERROR',
  context: undefined
}
```

### Affected versions

| Version range    | Needs minor update?                            |
|------------------|------------------------------------------------|
| `4.6.2...latest` | Nothing to do               |
| `3.0.0...4.6.1`  | Please upgrade to `socket.io@4.6.2` (at least) |
| `2.3.0...2.5.0`  | Please upgrade to `socket.io@2.5.1`            |

### Patches

This issue is fixed by https://github.com/socketio/socket.io/commit/15af22fc22bc6030fcead322c106f07640336115, included in `socket.io@4.6.2` (released in May 2023).

The fix was backported in the 2.x branch today: https://github.com/socketio/socket.io/commit/d30630ba10562bf987f4d2b42440fc41a828119c

### Workarounds

As a workaround for the affected versions of the `socket.io` package, you can attach a listener for the "error" event:

```js
io.on("connection", (socket) => {
  socket.on("error", () => {
    // ...
  });
});
```

### For more information

If you have any questions or comments about this advisory:

- Open a discussion [here](https://github.com/socketio/socket.io/discussions)

Thanks a lot to [Paul Taylor](https://github.com/Y0ursTruly) for the responsible disclosure.

### References

- https://github.com/socketio/socket.io/commit/15af22fc22bc6030fcead322c106f07640336115
- https://github.com/socketio/socket.io/commit/d30630ba10562bf987f4d2b42440fc41a828119c

## References
- https://github.com/socketio/socket.io/security/advisories/GHSA-25hc-qcg6-38wj
- https://nvd.nist.gov/vuln/detail/CVE-2024-38355
- https://github.com/socketio/socket.io/commit/15af22fc22bc6030fcead322c106f07640336115
- https://github.com/socketio/socket.io/commit/d30630ba10562bf987f4d2b42440fc41a828119c
- https://github.com/socketio/socket.io
