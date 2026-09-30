# [?] fix(wasmtesting): fix crash when deleting from nil map (#2382)

## Summary
Severity: Unknown
Chain: Cosmos
Component: CosmWasm/wasmd
Published: 2025-10-28
Source: https://github.com/CosmWasm/wasmd/commit/efc2eb5311cd115b2fb6968a8bb4ed56ef56854b
Type: security-commit

## Details
fix(wasmtesting): fix crash when deleting from nil map (#2382)

## Patch
### x/wasm/keeper/wasmtesting/mock_keepers.go
```diff
@@ -153,6 +153,9 @@ func (m *IBCContractKeeperMock) StoreAsyncAckPacket(ctx context.Context, packet
 }
 
 func (m *IBCContractKeeperMock) DeleteAsyncAckPacket(ctx context.Context, portID, channelID string, sequence uint64) {
+	if m.packets == nil {
+		return
+	}
 	key := portID + fmt.Sprint(len(channelID)) + channelID
 	delete(m.packets, key)
 }
```
