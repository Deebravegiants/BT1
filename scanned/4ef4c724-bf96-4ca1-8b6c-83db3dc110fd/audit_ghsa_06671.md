# [C] LaunchServer FileServerHandler has an unauthenticated path traversal issue

## Summary
Severity: Critical
Advisory: GHSA-5g75-477j-2c2f
CVE: CVE-2026-54617
CWE: CWE-200, CWE-22, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-5g75-477j-2c2f
Type: github-advisory

## Affected
- Maven: `pro.gravit.launcher:launchserver-api` — affected >=0

## Details
### Summary
An unauthenticated path traversal in the LaunchServer HTTP file server (`FileServerHandler`) lets any remote actor read **any file** readable by the LaunchServer process (e.g. `../../../../etc/passwd`). This is a generic arbitrary-file-read primitive, so the fix must address the traversal itself, not any specific file.

The readable files include the server's own secrets, which turns this from information disclosure into full compromise: the ECDSA private key that signs access JWTs (`.keys/ecdsa_id`), the refresh-token salt (`.keys/legacySalt`), and `LaunchServer.json` (database credentials). With the signing key an attacker mints a valid access token for any account, including admins. That is a full authentication bypass. Pre-auth, default config, port 9274.

**Affected:** GravitLauncher LaunchServer ≤ 5.7.11 (the LaunchServer application; the published `pro.gravit.launcher:*-api` Maven artifacts do not contain the vulnerable code).

### Details
In `FileServerHandler.channelRead0`:

```java
path = Paths.get(IOHelper.getPathFromUrlFragment(uri)).normalize().toString().substring(1); // line 194
File file = base.resolve(path).toFile();                                                     // line 200 - no second normalize()
```

`substring(1)` blindly strips a leading slash, assuming the request-target always starts with `/`. Netty's `HttpServerCodec` accepts a request-target **without** a leading slash verbatim (`decoderResult().isSuccess() == true`). For such a target, `normalize()` cannot collapse the leading `..`, `substring(1)` turns `../` into `./` (leaving the remaining `..`), and `base.resolve(path)`, which is not re-normalized, resolves **outside** `updatesDir`.

`file.isHidden()` (line 201) is checked only on the final path component, so targets that don't start with a dot (`ecdsa_id`, `rsa_id`, `legacySalt`, `LaunchServer.json`) are served even with `showHiddenFiles=false`.

The file server is enabled by default (`netty.fileServerEnabled=true`) and bound to `0.0.0.0:9274`. No auth handler precedes `FileServerHandler`; `WebSocketServerProtocolHandler("/api")` forwards non-WebSocket / non-`/api` requests down to it, so the attack is a plain HTTP GET (no WebSocket).

### PoC
Reproduced on a from-source build of v5.7.11 (Netty 4.2.12).
**Must use a raw socket.** curl/browsers/HTTP libraries normalize the path and prepend `/`, hitting the safe branch (false "not reproducible").

```
printf 'GET ../../.keys/ecdsa_id HTTP/1.1\r\nHost: x\r\n\r\n' | nc <host> 9274
```

Returns the raw ECDSA private-key bytes. Same for `../../.keys/rsa_id`, `../../.keys/legacySalt`, `../../LaunchServer.json`. `%2e%2e/...` (no leading slash) also works. Depth-robust arbitrary read: `../../../../../../etc/passwd`.
Control (confirms the root cause): `GET /../../.keys/ecdsa_id` (WITH leading slash) → 404. Only the no-leading-slash form escapes.

### Impact
Unauthenticated remote read of any file the process can access. What that exposes:
- `.keys/ecdsa_id`: the key that signs access JWTs. With it, an attacker mints a valid token for any account, including admins, so this is a full authentication bypass.
- `.keys/legacySalt`: lets an attacker forge refresh tokens.
- `LaunchServer.json`: database credentials.
- Any other file readable by the process (config, logs, system files).

Deployment note: a normalizing L7 reverse proxy (stock nginx `location / { proxy_pass ...; }`) rejects the no-leading-slash request (400) and collapses leading-slash traversal, blocking the primary vector. But the default bind is `0.0.0.0:9274`, so protection relies on firewalling the backend port; L4/TCP proxies (HAProxy TCP, nginx `stream`, CF Spectrum) and direct exposure remain exploitable.

### Suggested fix
1. Re-`normalize()` after `base.resolve(path)` and verify `resolved.startsWith(base)`.
2. Reject request-targets that don't start with `/` (400).
3. Default-bind to `127.0.0.1`; store `.keys` outside `updatesDir`.

## References
- https://github.com/GravitLauncher/Launcher/security/advisories/GHSA-5g75-477j-2c2f
- https://github.com/GravitLauncher/Launcher
