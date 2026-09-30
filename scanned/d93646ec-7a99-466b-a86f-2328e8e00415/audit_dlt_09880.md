# [?] Fix panic if account error (#4521)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2024-12-17
Source: https://github.com/iotexproject/iotex-core/commit/caa1c8ce54a5a5bb21b3e4576ad75c02a90d3bf9
Type: security-commit

## Details
Fix panic if account error (#4521)

Co-authored-by: CoderZhi <thecoderzhi@gmail.com>

## Patch
### api/web3server_utils.go
```diff
@@ -181,7 +181,10 @@ func (svr *web3Handler) checkContractAddr(to string) (bool, error) {
 		return false, err
 	}
 	accountMeta, _, err := svr.coreService.Account(ioAddr)
-	return accountMeta.IsContract, err
+	if err != nil {
+		return false, err
+	}
+	return accountMeta.IsContract, nil
 }
 
 func (svr *web3Handler) getLogsWithFilter(from uint64, to uint64, addrs []string, topics [][]string) ([]*getLogsResult, error) {
```
