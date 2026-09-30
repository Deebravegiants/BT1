# [?] eth/api: fix potential nil deref in AccountRange (#21710)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2020-10-20
Source: https://github.com/ethereum/go-ethereum/commit/3e82c9ef67b9948bc90ba244b9537054188ebaf8
Type: security-commit

## Details
eth/api: fix potential nil deref in AccountRange (#21710)

* Fix potential nil pointer error when neither block number nor hash is specified to accountRange

* Update error description

## Patch
### eth/api.go
```diff
@@ -389,6 +389,8 @@ func (api *PublicDebugAPI) AccountRange(blockNrOrHash rpc.BlockNumberOrHash, sta
 		if err != nil {
 			return state.IteratorDump{}, err
 		}
+	} else {
+		return state.IteratorDump{}, errors.New("either block number or block hash must be specified")
 	}
 
 	if maxResults > AccountRangeMaxResults || maxResults <= 0 {
```
