# [?] TxPool: Fix panic in the `TransactionPool` (#14057)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-03-04
Source: https://github.com/erigontech/erigon/commit/a1559ec0fa34e1a628a36dc9e9a61c0870cfa683
Type: security-commit

## Details
TxPool: Fix panic in the `TransactionPool` (#14057)

## Patch
### txnprovider/txpool/txpoolcfg/txpoolcfg.go
```diff
@@ -182,6 +182,8 @@ func (r DiscardReason) String() string {
 		return "blobs limit in txpool is full"
 	case NoAuthorizations:
 		return "EIP-7702 transactions with an empty authorization list are invalid"
+	case GasLimitTooHigh:
+		return "gas limit is too high"
 	default:
 		panic(fmt.Sprintf("discard reason: %d", r))
 	}
```
