# [?] fix(privval): Ephemeral Port Exhaustion (#5433)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2025-11-17
Source: https://github.com/cometbft/cometbft/commit/8f382edb9bafecf04dfce78fe80fe53cca7125f8
Type: security-commit

## Details
fix(privval): Ephemeral Port Exhaustion (#5433)

## Ephemeral Port Exhaustion of `priv_validator_laddr`

While conducting automated security scanning on our Cosmos based
infrastructure we noticed after some time the `priv_validator_laddr`
would stop accepting new connections. On investigation it appears that
the connection is not properly closed after a failed connection attempt
eventually exhausting all ephemeral ports. It appears the method
`MakeSecretConnection` doesn't close the connection and leaves it in a
`CLOSE_WAIT` state.

## Steps to Reproduce

The following script connects to the `priv_validator_laddr` and
disconnects. After ~2000 requests the port will stop accepting new
connections and the service will require restarting to free the ports.

```python
#!/usr/bin/env python3
import socket

ip_address = '10.10.10.10'
priv_val_port = 1234
runs = 10000

def tcp_probe(ip, port, timeout=2):
    """Connect to priv_val_port and immediately close the connection"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        if s.connect_ex((ip, port)) == 0:
            return True
        else:
            return False
    finally:
        s.close()

def main():
    for i in range(runs):
        connected = tcp_probe(ip_address, priv_val_port)
        if connected:
            print(f"Completed probe {i+1}/{runs}")
        else:
            print(f"Probe failed {i+1}/{runs}")

main()

```

The ports are left in a `CLOSE_WAIT` state which can be viewed with
`netstat -anp | grep CLOSE_WAIT` and do not clear until the service is
restarted.

## Proposed Solution

In the event of an error during the call to `MakeSecretConnection` call
`tc.Close()`.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Close `timeoutConn` when `MakeSecretConnection` fails in
`privval/socket_listeners.go` to avoid `CLOSE_WAIT`/ephemeral port
exhaustion; update CHANGELOG.
>
> - **Bug Fix (privval)**
> - Close `timeoutConn` if `p2pconn.MakeSecretConnection` returns an
error in `privval/socket_listeners.go#TCPListener.Accept`, preventing
leaked sockets (`CLOSE_WAIT`).
> - **Docs**
> - Update `CHANGELOG.md` under BUG FIXES to note the privval ephemeral
port exhaustion fix.
>
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
32708b787bfd074959ddba0c94bb61189e8a0cb0. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

### CHANGELOG.md
```diff
@@ -6,7 +6,11 @@
 
 ### BUG FIXES
 
+- `[p2p]` fix(privval): Ephemeral Port Exhaustion
+  ([\#5433](https://github.com/cometbft/cometbft/pull/5433))
+
 ### IMPROVEMENTS
+
 -  `[mempool]` perf(mempool/cache): Optimize LRUTxCache.Remove to reduce lock contention and map access
    ([\#5244](https://github.com/cometbft/cometbft/pull/5244))
 - `[e2e]` add support for testing different keytypes, including BLS
```

### privval/socket_listeners.go
```diff
@@ -78,6 +78,7 @@ func (ln *TCPListener) Accept() (net.Conn, error) {
 	timeoutConn := newTimeoutConn(tc, ln.timeoutReadWrite)
 	secretConn, err := p2pconn.MakeSecretConnection(timeoutConn, ln.secretConnKey)
 	if err != nil {
+		_ = timeoutConn.Close()
 		return nil, err
 	}
 
```
