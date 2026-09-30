# [?] deadlock fix

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-10-03
Source: https://github.com/0xsoniclabs/sonic/commit/775de821a734c11986f641a33e54c05c2c086045
Type: security-commit

## Details
deadlock fix

## Patch
### kvdb/flushable/synced_pool.go
```diff
@@ -99,9 +99,6 @@ func (p *SyncedPool) GetDb(name string) kvdb.KeyValueStore {
 }
 
 func (p *SyncedPool) getDb(name string) kvdb.KeyValueStore {
-	p.mutex.Lock()
-	defer p.mutex.Unlock()
-
 	if wrapper := p.wrappers[name]; wrapper != nil {
 		return wrapper
 	}
```
