# [?] fix: panic: assignment to entry in nil map (#2513)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2020-11-19
Source: https://github.com/iotexproject/iotex-core/commit/13e8192aa4ead8f38000c3a837de667ddb1677c4
Type: security-commit

## Details
fix: panic: assignment to entry in nil map (#2513)

panic when subLogs is configured

## Patch
### pkg/log/log.go
```diff
@@ -50,6 +50,7 @@ func init() {
 	}
 	_logMu.Lock()
 	_globalCfg.Zap = &zapCfg
+	_subLoggers = make(map[string]*zap.Logger)
 	_logMu.Unlock()
 	zap.ReplaceGlobals(l)
 }
```
