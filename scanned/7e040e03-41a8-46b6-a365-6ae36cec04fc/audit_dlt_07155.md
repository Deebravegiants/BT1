# [?] btcd: fix getblock panic triggered by rpc call

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2026-09-08
Source: https://github.com/btcsuite/btcd/commit/56653a0bc22475096880007de1abcd05681bcfe6
Type: security-commit

## Details
btcd: fix getblock panic triggered by rpc call

As stated on issue #2597, a JSONRPC request containing `null` as value
for `GetBlockCmd.Verbosity` causes a panic in the `handleGetBlock`
procedure.

This commit fixes it by setting the default value of `1` when `Verbosity` is
`nil` in the start of the `handleGetBlock` procedure.

## Patch
### rpcserver.go
```diff
@@ -1074,6 +1074,10 @@ func getDifficultyRatio(bits uint32, params *chaincfg.Params) float64 {
 // handleGetBlock implements the getblock command.
 func handleGetBlock(s *rpcServer, cmd interface{}, closeChan <-chan struct{}) (interface{}, error) {
 	c := cmd.(*btcjson.GetBlockCmd)
+	if c.Verbosity == nil {
+		c.Verbosity = new(int)
+		*c.Verbosity = 1
+	}
 
 	// Load the raw block bytes from the database.
 	hash, err := chainhash.NewHashFromStr(c.Hash)
@@ -1116,7 +1120,7 @@ func handleGetBlock(s *rpcServer, cmd interface{}, closeChan <-chan struct{}) (i
 	}
 
 	// If verbosity is 0, return the serialized block as a hex encoded string.
-	if c.Verbosity != nil && *c.Verbosity == 0 {
+	if *c.Verbosity == 0 {
 		return hex.EncodeToString(blkBytes), nil
 	}
 
```
