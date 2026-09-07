# [C] NornicDB has Improper Network Binding in its Bolt Server, allowing unauthorized remote access

## Summary
Severity: Critical
Advisory: GHSA-2hp7-65r3-wv54
CVE: CVE-2026-42072
CWE: CWE-1392
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-2hp7-65r3-wv54
Type: github-advisory

## Affected
- Go: `github.com/orneryd/nornicdb` — affected >=0 <1.0.42-hotfix

## Details
## Summary

The `--address` CLI flag (and `NORNICDB_ADDRESS` / `server.host` config key) is plumbed through to the HTTP server correctly but **never reaches the Bolt server config**. The Bolt listener therefore always binds to the wildcard address (all interfaces), regardless of what the user configures.

On a LAN, this exposes the graph database — with its default `admin:password` credentials — to any device sharing the network.

## Version

- `nornicdb v1.0.39`
- Built from commit `afe7c9d` on `main`
- Platform: macOS (darwin 25.4.0, arm64)

## Reproduction

```
$ nornicdb serve --address 127.0.0.1 --bolt-port 7687 --http-port 7474 ...
```

Output claims Bolt is on localhost:
```
Bolt server listening on bolt://localhost:7687
```

But the actual socket:
```
$ netstat -an -p tcp | grep 7687
tcp46      0      0  *.7687                 *.*                    LISTEN

$ lsof -iTCP:7687 -sTCP:LISTEN -n -P
nornicdb ... IPv6 ... TCP *:7687 (LISTEN)
```

HTTP port is correctly bound:
```
tcp4  127.0.0.1.7474   *.*  LISTEN
```

Reachable from another host on the LAN:
```
$ nc -z 192.168.x.y 7687
Connection to 192.168.x.y port 7687 [tcp/*] succeeded!
```

Setting `NORNICDB_BOLT_ADDRESS=127.0.0.1` or `server.host: "127.0.0.1"` in `config.yaml` has **no effect** on the Bolt listener.

## Root Cause

In `pkg/bolt/server.go:774-776`:

```go
func (s *Server) ListenAndServe() error {
    addr := fmt.Sprintf(":%d", s.config.Port)
    listener, err := net.Listen("tcp", addr)
    ...
}
```

`bolt.Config` (line 474) has no `Host`/`Address`/`Addr` field — only `Port`. The CLI flag `--address` is stored in a local variable in `cmd/nornicdb/main.go:80` and used to format user-facing log output (line 637–644), but is never copied into `boltConfig` at line 600–609 when Bolt is initialized.

Since `ListenAndServe` calls `net.Listen("tcp", ":7687")` with an empty host, Go binds the wildcard socket on all interfaces.

## Suggested Fix

1. Add a `Host string` field to `bolt.Config` (default `"127.0.0.1"`, matching the CLI flag default).
2. In `cmd/nornicdb/main.go` around line 601, wire it through:
   ```go
   boltConfig.Host = address
   boltConfig.Port = boltPort
   ```
3. In `pkg/bolt/server.go:775`, use the host:
   ```go
   addr := net.JoinHostPort(s.config.Host, strconv.Itoa(s.config.Port))
   ```

## Security Impact

- Default `admin:password` credentials + wildcard binding = anyone on the same WiFi can issue arbitrary Cypher queries (read, write, delete nodes) against NornicDB instances running with default setup.
- Users following the README will reasonably assume `--address 127.0.0.1` (the documented default) binds *both* protocols to localhost.
- Workaround: host-firewall rules (e.g. macOS `pf`) blocking non-loopback → 7687. Not discoverable from the docs.

## References
- https://github.com/orneryd/NornicDB/security/advisories/GHSA-2hp7-65r3-wv54
- https://nvd.nist.gov/vuln/detail/CVE-2026-42072
- https://github.com/orneryd/NornicDB/commit/adce4f9a9fc7b6aada07c0bfa2d737cd7a6efaca
- https://github.com/orneryd/NornicDB
- https://github.com/orneryd/NornicDB/releases/tag/v1.0.42
- https://github.com/orneryd/NornicDB/releases/tag/v1.0.42-hotfix
