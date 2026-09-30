# [?] core/state: fix panic in state dumping (#22225)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-01-26
Source: https://github.com/ethereum/go-ethereum/commit/14d495491ddf31464135563720705fc2c1e5eb22
Type: security-commit

## Details
core/state: fix panic in state dumping (#22225)

## Patch
### core/state/dump.go
```diff
@@ -138,7 +138,7 @@ func (s *StateDB) DumpToCollector(c DumpCollector, excludeCode, excludeStorage,
 			account.SecureKey = it.Key
 		}
 		addr := common.BytesToAddress(addrBytes)
-		obj := newObject(nil, addr, data)
+		obj := newObject(s, addr, data)
 		if !excludeCode {
 			account.Code = common.Bytes2Hex(obj.Code(s.db))
 		}
```
