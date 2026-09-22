# [M] engine.io Uncaught Exception vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q9mw-68c2-j6m5
CVE: CVE-2023-31125
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-03
Source: https://github.com/advisories/GHSA-q9mw-68c2-j6m5
Type: github-advisory

## Affected
- npm: `engine.io` — affected >=5.1.0 <6.4.2

## Details
### Impact

A specially crafted HTTP request can trigger an uncaught exception on the Engine.IO server, thus killing the Node.js process.

```
TypeError: Cannot read properties of undefined (reading 'handlesUpgrades')
    at Server.onWebSocket (build/server.js:515:67)
```

This impacts all the users of the [`engine.io`](https://www.npmjs.com/package/engine.io) package, including those who uses depending packages like [`socket.io`](https://www.npmjs.com/package/socket.io).

### Patches

A fix has been released today (2023/05/02): [6.4.2](https://github.com/socketio/engine.io/releases/tag/6.4.2)

This bug was introduced in version 5.1.0 and included in version 4.1.0 of the `socket.io` parent package. Older versions are not impacted.

For `socket.io` users:

| Version range               | `engine.io` version | Needs minor update?                                                                                    |
|-----------------------------|---------------------|--------------------------------------------------------------------------------------------------------|
| `socket.io@4.6.x`           | `~6.4.0`            | `npm audit fix` should be sufficient                                                                   |
| `socket.io@4.5.x`           | `~6.2.0`            | Please upgrade to `socket.io@4.6.x`                                                                    |
| `socket.io@4.4.x`           | `~6.1.0`            | Please upgrade to `socket.io@4.6.x`                                                                    |
| `socket.io@4.3.x`           | `~6.0.0`            | Please upgrade to `socket.io@4.6.x`                                                                    |
| `socket.io@4.2.x`           | `~5.2.0`            | Please upgrade to `socket.io@4.6.x`                                                                    |
| `socket.io@4.1.x`           | `~5.1.1`            | Please upgrade to `socket.io@4.6.x`                                                                    |
| `socket.io@4.0.x`           | `~5.0.0`            | Not impacted |
| `socket.io@3.1.x`           | `~4.1.0`            | Not impacted |
| `socket.io@3.0.x`           | `~4.0.0`            | Not impacted |
| `socket.io@2.5.0`           | `~3.6.0`            | Not impacted |
| `socket.io@2.4.x` and below | `~3.5.0`            | Not impacted |

### Workarounds

There is no known workaround except upgrading to a safe version.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [`engine.io`](https://github.com/socketio/engine.io)

Thanks to Thomas Rinsma from Codean for the responsible disclosure.

## References
- https://github.com/socketio/engine.io/security/advisories/GHSA-q9mw-68c2-j6m5
- https://nvd.nist.gov/vuln/detail/CVE-2023-31125
- https://github.com/socketio/engine.io/commit/fc480b4f305e16fe5972cf337d055e598372dc44
- https://github.com/socketio/engine.io
- https://github.com/socketio/engine.io/releases/tag/6.4.2
- https://security.netapp.com/advisory/ntap-20230622-0002
