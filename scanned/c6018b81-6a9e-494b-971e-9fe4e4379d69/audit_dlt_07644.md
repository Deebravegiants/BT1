# [?] les: fix clientInfo deadlock (#20395)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2019-11-26
Source: https://github.com/ethereum/go-ethereum/commit/878e35bfde7c1911857622ed7fd19ad9827114f9
Type: security-commit

## Details
les: fix clientInfo deadlock (#20395)

## Patch
### les/api.go
```diff
@@ -108,7 +108,7 @@ func (api *PrivateLightServerAPI) clientInfo(c *clientInfo, id enode.ID) map[str
 		info["priority"] = pb != 0
 	} else {
 		info["isConnected"] = false
-		pb := api.server.clientPool.getPosBalance(id)
+		pb := api.server.clientPool.ndb.getOrNewPB(id)
 		info["pricing/balance"], info["pricing/balanceMeta"] = pb.value, pb.meta
 		info["priority"] = pb.value != 0
 	}
```
