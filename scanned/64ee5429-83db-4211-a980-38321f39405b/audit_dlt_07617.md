# [?] rpc: avoid crashing on clique getSigner during sync (#23832)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-11-01
Source: https://github.com/ethereum/go-ethereum/commit/ff844918e806cf1337606b4aafdaefbf6d579a9a
Type: security-commit

## Details
rpc: avoid crashing on clique getSigner during sync (#23832)

## Patch
### consensus/clique/api.go
```diff
@@ -214,6 +214,9 @@ func (api *API) GetSigner(rlpOrBlockNr *blockNumberOrHashOrRLP) (common.Address,
 		} else if number, ok := blockNrOrHash.Number(); ok {
 			header = api.chain.GetHeaderByNumber(uint64(number.Int64()))
 		}
+		if header == nil {
+			return common.Address{}, fmt.Errorf("missing block %v", blockNrOrHash.String())
+		}
 		return api.clique.Author(header)
 	}
 	block := new(types.Block)
```

### rpc/types.go
```diff
@@ -186,6 +186,16 @@ func (bnh *BlockNumberOrHash) Number() (BlockNumber, bool) {
 	return BlockNumber(0), false
 }
 
+func (bnh *BlockNumberOrHash) String() string {
+	if bnh.BlockNumber != nil {
+		return strconv.Itoa(int(*bnh.BlockNumber))
+	}
+	if bnh.BlockHash != nil {
+		return bnh.BlockHash.String()
+	}
+	return "nil"
+}
+
 func (bnh *BlockNumberOrHash) Hash() (common.Hash, bool) {
 	if bnh.BlockHash != nil {
 		return *bnh.BlockHash, true
```
