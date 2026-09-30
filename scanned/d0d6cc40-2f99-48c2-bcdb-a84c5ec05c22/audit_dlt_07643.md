# [?] cmd/faucet: protect f.reqs with Rlock to prevent data race (#20669)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2020-02-15
Source: https://github.com/ethereum/go-ethereum/commit/37531b18847774a7f057496bc34f2a48053fa417
Type: security-commit

## Details
cmd/faucet: protect f.reqs with Rlock to prevent data race (#20669)

* cmd/faucet: add Rlock to protect f.reqs in apiHandler

* cmd/faucet: make a locked copy of f.reqs

## Patch
### cmd/faucet/faucet.go
```diff
@@ -360,11 +360,14 @@ func (f *faucet) apiHandler(w http.ResponseWriter, r *http.Request) {
 		}
 	}
 	// Send over the initial stats and the latest header
+	f.lock.RLock()
+	reqs := f.reqs
+	f.lock.RUnlock()
 	if err = send(conn, map[string]interface{}{
 		"funds":    new(big.Int).Div(balance, ether),
 		"funded":   nonce,
 		"peers":    f.stack.Server().PeerCount(),
-		"requests": f.reqs,
+		"requests": reqs,
 	}, 3*time.Second); err != nil {
 		log.Warn("Failed to send initial stats to client", "err", err)
 		return
```
