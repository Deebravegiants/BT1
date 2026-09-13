# [H] Socket.IO: Engine.IO WebTransport SID DoS

## Summary
Severity: High
Advisory: GHSA-gr94-w7qr-f4j3
CVE: CVE-2026-59724
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-31
Source: https://github.com/advisories/GHSA-gr94-w7qr-f4j3
Type: github-advisory

## Affected
- npm: `engine.io` — affected >=6.5.0 <6.6.7

## Details
### Impact

Engine.IO servers with **WebTransport enabled** are vulnerable to a remotely triggerable denial of service.

A malicious unauthenticated client can send a crafted WebTransport upgrade request containing a specially chosen session ID, such as `__proto__`. Because the session ID lookup did not properly verify that the key was an own property of the clients object, the lookup could resolve to an inherited prototype property instead of a valid Engine.IO client.

This can cause a `TypeError` during WebTransport upgrade handling. Since the failure occurs in an asynchronous context, it may result in an unhandled Promise rejection and terminate the Node.js process on affected Node.js versions/configurations.

Successful exploitation can allow an unauthenticated remote attacker to crash the server process and cause denial of service. Under a process supervisor, repeated exploitation may cause crash loops.

Affected configurations are limited to deployments where WebTransport support is enabled. WebTransport is not enabled by default.

Affected versions:

- `engine.io >= 6.5.0 < 6.6.7`

## Patches

The issue was fixed in:

- **engine.io 6.6.7**

Users should upgrade to `engine.io@6.6.7` or later.

If using Socket.IO packages that depend on Engine.IO, users should update to a Socket.IO release that includes the patched Engine.IO version.

### Workarounds

If upgrading immediately is not possible, affected users can mitigate the issue by disabling WebTransport support.

WebTransport is opt-in, so servers should ensure that `webtransport` is not included in the enabled transports list.

For example, use only the default HTTP long-polling and WebSocket transports:

```js
const engine = new Server({
  transports: ["polling", "websocket"],
});
```

Additional operational mitigations may include:

- Restricting access to WebTransport endpoints at the reverse proxy or HTTP/3 layer.
- Disabling HTTP/3/WebTransport support until the patched version can be deployed.
- Running the service under a supervisor as a partial availability mitigation, though this does not prevent repeated crash attempts.

### References

- Fix commit: https://github.com/socketio/socket.io/commit/1fa1f46cd420ac5b57bb4c04c959b58f3c79158c
- Engine.IO changelog entry for `6.6.7`: https://github.com/socketio/socket.io/blob/main/packages/engine.io/CHANGELOG.md#667-2026-04-27
- Engine.IO package: https://www.npmjs.com/package/engine.io
- Socket.IO repository: https://github.com/socketio/socket.io

## References
- https://github.com/socketio/socket.io/security/advisories/GHSA-gr94-w7qr-f4j3
- https://nvd.nist.gov/vuln/detail/CVE-2026-59724
- https://github.com/socketio/socket.io/commit/1fa1f46cd420ac5b57bb4c04c959b58f3c79158c
- https://github.com/socketio/socket.io
- https://github.com/socketio/socket.io/releases/tag/engine.io@6.6.7
