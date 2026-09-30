# [?] fix panic when reuseport was no available

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2017-03-24
Source: https://github.com/libp2p/go-libp2p/commit/53da0c05ceeb11e00c72639584447eb99b23c8e8
Type: security-commit

## Details
fix panic when reuseport was no available

## Patch
### p2p/transport/tcp/tcp.go
```diff
@@ -172,6 +172,7 @@ func (t *TcpTransport) newTcpDialer(base manet.Dialer, laddr ma.Multiaddr, doReu
 	return &tcpDialer{
 		doReuse:   false,
 		laddr:     laddr,
+		pattern:   pattern,
 		madialer:  base,
 		transport: t,
 	}, nil
```
