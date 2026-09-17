# [C] Linkdave Missing Authentication on REST and WebSocket endpoints

## Summary
Severity: Critical
Advisory: GHSA-xv8g-fj9h-6gmv
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-xv8g-fj9h-6gmv
Type: github-advisory

## Affected
- Go: `github.com/shi-gg/linkdave` — affected >=0 <0.1.5

## Details
The `linkdave` server does not enforce authentication on its REST and WebSocket routes in versions prior to `0.1.5`.

### Impact

An attacker with network access to the server port can:
- Connect to the WebSocket endpoint (`/ws`) and receive a valid `session_id` in the `OpReady` response.
- Use that session to invoke all REST player controls on any guild corresponding to their session id[1].
- Enumerate server statistics and runtime information via the unauthenticated `/stats` endpoint (still public after the fix).

[1] If on [`>=0.1.0`](https://github.com/shi-gg/linkdave/releases/tag/v0.1.0), attackers are restricted to creating, controlling and deleting players created within their own session ID.

### Vulnerable Routes

The following routes were entirely unauthenticated in `>= 0.0.1, < 0.1.5`:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/sessions/{session_id}/players/{guild_id}/play` | Start audio playback |
| `POST` | `/sessions/{session_id}/players/{guild_id}/pause` | Pause playback |
| `POST` | `/sessions/{session_id}/players/{guild_id}/resume` | Resume playback |
| `POST` | `/sessions/{session_id}/players/{guild_id}/stop` | Stop playback |
| `POST` | `/sessions/{session_id}/players/{guild_id}/seek` | Seek to position |
| `PATCH` | `/sessions/{session_id}/players/{guild_id}/volume` | Set volume |
| `DELETE` | `/sessions/{session_id}/players/{guild_id}` | Disconnect from voice channel |
| `GET` | `/ws` | WebSocket event stream |

### Patches

Update to [`0.1.5`](https://github.com/shi-gg/linkdave/commit/0f9a00d9d549b16278db81fce6dfec350c2abc01).

```diff
- image: ghcr.io/shi-gg/linkdave:0.1.4
+ image: ghcr.io/shi-gg/linkdave:latest
```
or
```sh
docker pull ghcr.io/shi-gg/linkdave:latest
```

After upgrading, set the `LINKDAVE_PASSWORD` environment variable to a strong secret value. If this variable is left unset, the server will still accept all connections without authentication even on `>= 0.1.5`.

**Server configuration (e.g. `compose.yml`):**
```sh
environment:
    LINKDAVE_PASSWORD: ${LINKDAVE_PASSWORD}
```
```sh
echo "LINKDAVE_PASSWORD=$(openssl rand -hex 16)" >> .env
```

To restart the stack, run
```sh
docker compose up -d
```

**TypeScript client (`0.1.5+`):**

The client automatically handles authentication. Pass the password when constructing the client:
```ts
const linkdave = new LinkDaveClient({
    nodes: [
        {
            name: "main",
            url: process.env.LINKDAVE_URI,
            password: process.env.LINKDAVE_PASSWORD
        }
    ]
});
```

### Workarounds

If upgrading is not immediately possible, restrict network access to the server's port using a firewall so it is only accessible from trusted internal IP addresses.

## References
- https://github.com/shi-gg/linkdave/security/advisories/GHSA-xv8g-fj9h-6gmv
- https://github.com/shi-gg/linkdave/commit/0f9a00d9d549b16278db81fce6dfec350c2abc01
- https://github.com/shi-gg/linkdave
