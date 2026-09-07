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

```

_Trimmed to 38 lines — full report: https://github.com/cometbft/cometbft/commit/8f382edb9bafecf04dfce78fe80fe53cca7125f8_
