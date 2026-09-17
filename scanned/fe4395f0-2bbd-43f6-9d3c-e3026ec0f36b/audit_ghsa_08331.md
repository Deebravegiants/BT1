# [H] goshs: SSH host key verification disabled, allowing transparent MITM of every tunnelled HTTP request

## Summary
Severity: High
Advisory: GHSA-mxg3-432p-mr72
CWE: CWE-295, CWE-322
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-mxg3-432p-mr72
Type: github-advisory

## Affected
- Go: `goshs.de/goshs/v2` — affected >=0 <2.0.7

## Details
### Summary

The `--tunnel` / `-t` flag opens an outbound SSH connection to `localhost.run:22` with `HostKeyCallback: ssh.InsecureIgnoreHostKey()`. The Go documentation for that function states verbatim: *"It should not be used for production code."* With the callback disabled the client accepts any host key the server presents, so an attacker who can intercept the operator's TCP connection to `localhost.run:22` (any router on the path, malicious local network, ARP/DNS spoof on the operator's LAN, BGP hijack, malicious VPN) can present their own SSH host key, terminate the SSH session locally, and proxy onward — sitting transparently in the middle of the tunnel.

Because `localhost.run` does TLS termination at their end, the HTTP traffic on the SSH leg is plaintext, so the on-path attacker reads and rewrites every request and response in cleartext. The goshs operator gets no warning; the public URL works normally.

### Affected Code

**File:** `tunnel/tunnel.go`

```go
func Start(localIP string, localPort int) (*Tunnel, error) {
    config := &ssh.ClientConfig{
        User:            "nokey",
        Auth:            []ssh.AuthMethod{ssh.Password("")},
        HostKeyCallback: ssh.InsecureIgnoreHostKey(), // accepts any server key
        Timeout:         10 * time.Second,
        BannerCallback:  func(banner string) error { return nil },
    }
    client, err := ssh.Dial("tcp", "localhost.run:22", config)
    ...
}
```

There is no fallback verification — no `ssh.FixedHostKey`, no `known_hosts` read, no TOFU pin. Every invocation of `goshs --tunnel` is equally vulnerable.

### Exploit Chain

1. Operator runs `goshs --tunnel`. `tunnel.Start()` opens an SSH client to `localhost.run:22` with `InsecureIgnoreHostKey()`.
2. Attacker positioned on the network path (compromised router, café Wi-Fi MITM, malicious VPN exit, hostile ISP, BGP hijack, or `arpspoof` + DNS spoof on the operator's LAN) intercepts the outbound TCP connection to `localhost.run:22` and answers with their own SSH server.
3. The attacker's fake SSH server presents an attacker-generated host key. The goshs client's `HostKeyCallback` returns nil unconditionally. Handshake completes; the client believes it is talking to `localhost.run`.
4. The attacker proxies the SSH session onward to the real `localhost.run:22`, forwarding the URL capture so `Start()` reads back the genuine `https://*.lhr.life` line and returns successfully. The operator sees the public URL printed to stdout exactly as expected.
5. Every HTTP request arriving at the public URL is routed over the SSH session. The attacker reads every URL, query string, header, body, and `Authorization` value sent by every visitor.
6. For each response the attacker can rewrite the body or headers — serving modified files, injecting HTML/JS, redirecting requests, or stripping `Set-Cookie` attributes.
7. Captured basic-auth credentials give the attacker authenticated access to upload, share-link, catcher, clipboard, and CLI endpoints. If goshs is running credential-collection listeners (SMB/LDAP/SMTP), the captured NTLM hashes and SMTP messages flowing through the tunnel are also exposed.

### Impact

- **Confidentiality (High):** all HTTP request and response content is readable by the on-path attacker (URLs, headers, basic-auth `Authorization`, file contents, share-link tokens, the `?goshs-info` JSON dump).
- **Integrity (High):** attacker can modify responses in-flight — replace served files, inject `<script>` into HTML responses, swap offered binaries for backdoored ones.
- **Availability:** not affected.

### Preconditions

- Operator must be running `goshs --tunnel` / `goshs -t`.
- Attacker must hold a network-on-path position between the operator and `localhost.run:22` (LAN MITM, malicious Wi-Fi, hostile ISP/VPN, BGP hijack, or DNS spoofing combined with an attacker-controlled SSH endpoint).

---

### Fix (applied in v2.0.7)

`ssh.InsecureIgnoreHostKey()` has been replaced with a **Trust-On-First-Use (TOFU)** host key callback backed by `~/.config/goshs/known_hosts`.

**Behaviour after the fix:**

- On **first connection**: goshs accepts the host key presented by `localhost.run`, writes it to `~/.config/goshs/known_hosts` (mode `0600`), and prints two warning lines:
  ```
  WARN  tunnel: pinned new host key for localhost.run:22 (SHA256:<fingerprint>) in ~/.config/goshs/known_hosts
  WARN  tunnel: verify with: ssh-keyscan localhost.run 2>/dev/null | ssh-keygen -l -f -
  ```
  The operator should compare the printed fingerprint against the `ssh-keyscan` output to confirm no MITM occurred on that first connection.

- On **subsequent connections**: the stored key is loaded via `golang.org/x/crypto/ssh/knownhosts` and the presented key is verified against it. A mismatch returns a typed `HostKeyMismatchError` and goshs exits immediately with:
  ```
  FATAL tunnel: ssh: host key mismatch for localhost.run:22 — possible MITM attack.
        If localhost.run legitimately rotated its key, delete ~/.config/goshs/known_hosts and reconnect
  ```

**Files changed:**

| File | Change |
|------|--------|
| `config/config.go` | Added `Dir()` — creates and returns `~/.config/goshs` (mode `0700`) |
| `main.go` | Calls `config.Dir()` on every startup to ensure the directory exists |
| `tunnel/tunnel.go` | Replaced `InsecureIgnoreHostKey()` with `buildTOFUCallback(knownHostsFile)`; added exported `HostKeyMismatchError` type |
| `httpserver/server.go` | Resolves `~/.config/goshs/known_hosts` via `config.Dir()`, passes it to `tunnel.Start()`; fatal-exits on `HostKeyMismatchError` |

**Implementation uses only already-vendored dependencies** (`golang.org/x/crypto/ssh/knownhosts` is part of the existing `golang.org/x/crypto` direct dependency — no new modules added).

## References
- https://github.com/patrickhener/goshs/security/advisories/GHSA-mxg3-432p-mr72
- https://github.com/patrickhener/goshs/commit/8f409cb08aacc6e94704334e8b1fb2cd50f5dd98
- https://github.com/patrickhener/goshs
- https://github.com/patrickhener/goshs/releases/tag/v2.0.7
