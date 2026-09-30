# [?] quic: fix race condition in TestClientCanDialDifferentQUICVersions (#1937)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2022-12-08
Source: https://github.com/libp2p/go-libp2p/commit/2c82176c35be49a887482382c2056a27a727c7d3
Type: security-commit

## Details
quic: fix race condition in TestClientCanDialDifferentQUICVersions (#1937)

## Patch
### p2p/transport/quic/conn_test.go
```diff
@@ -758,7 +758,6 @@ func TestClientCanDialDifferentQUICVersions(t *testing.T) {
 						panic("unexpected version")
 					}
 					require.NoError(t, err)
-					defer conn.Close()
 
 					_, versionConnLocal, err := quicreuse.FromQuicMultiaddr(conn.LocalMultiaddr())
 					require.NoError(t, err)
```
