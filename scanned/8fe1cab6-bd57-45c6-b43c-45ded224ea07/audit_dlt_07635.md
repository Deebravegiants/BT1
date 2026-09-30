# [?] metrics: fix the panic for reading empty cpu stats (#21864)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2020-11-18
Source: https://github.com/ethereum/go-ethereum/commit/b9ff57c59e3705eb963d39001192ab3a0ecd2d1e
Type: security-commit

## Details
metrics: fix the panic for reading empty cpu stats (#21864)

## Patch
### metrics/cpu_enabled.go
```diff
@@ -31,6 +31,10 @@ func ReadCPUStats(stats *CPUStats) {
 		log.Error("Could not read cpu stats", "err", err)
 		return
 	}
+	if len(timeStats) == 0 {
+		log.Error("Empty cpu stats")
+		return
+	}
 	// requesting all cpu times will always return an array with only one time stats entry
 	timeStat := timeStats[0]
 	stats.GlobalTime = int64((timeStat.User + timeStat.Nice + timeStat.System) * cpu.ClocksPerSec)
```
