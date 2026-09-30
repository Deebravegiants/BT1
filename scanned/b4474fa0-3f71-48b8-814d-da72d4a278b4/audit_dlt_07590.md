# [?] eth: fix crash on querying finalized block (#27162)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2023-04-25
Source: https://github.com/ethereum/go-ethereum/commit/b1113aa07ee554575be9276b862fd786d1db52be
Type: security-commit

## Details
eth: fix crash on querying finalized block (#27162)

eth: fix crash on querying nil finalized block

## Patch
### eth/api_backend.go
```diff
@@ -134,13 +134,19 @@ func (b *EthAPIBackend) BlockByNumber(ctx context.Context, number rpc.BlockNumbe
 			return nil, errors.New("'finalized' tag not supported on pre-merge network")
 		}
 		header := b.eth.blockchain.CurrentFinalBlock()
+		if header == nil {
+			return nil, errors.New("finalized block not found")
+		}
 		return b.eth.blockchain.GetBlock(header.Hash(), header.Number.Uint64()), nil
 	}
 	if number == rpc.SafeBlockNumber {
 		if !b.eth.Merger().TDDReached() {
 			return nil, errors.New("'safe' tag not supported on pre-merge network")
 		}
 		header := b.eth.blockchain.CurrentSafeBlock()
+		if header == nil {
+			return nil, errors.New("safe block not found")
+		}
 		return b.eth.blockchain.GetBlock(header.Hash(), header.Number.Uint64()), nil
 	}
 	return b.eth.blockchain.GetBlockByNumber(uint64(number)), nil
```
