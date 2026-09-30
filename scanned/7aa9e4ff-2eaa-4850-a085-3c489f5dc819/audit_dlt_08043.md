# [?] swarm/shed: fix a deadlock in meter function (#19149)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-02-21
Source: https://github.com/celo-org/celo-blockchain/commit/c8da76e63d1d873a4272e1d05231f8a13bf730bf
Type: security-commit

## Details
swarm/shed: fix a deadlock in meter function (#19149)

## Patch
### swarm/shed/db.go
```diff
@@ -23,7 +23,6 @@
 package shed
 
 import (
-	"errors"
 	"fmt"
 	"strconv"
 	"strings"
@@ -56,7 +55,7 @@ type DB struct {
 	diskReadMeter    metrics.Meter // Meter for measuring the effective amount of data read
 	diskWriteMeter   metrics.Meter // Meter for measuring the effective amount of data written
 
-	quitChan chan chan error // Quit channel to stop the metrics collection before closing the database
+	quit chan struct{} // Quit channel to stop the metrics collection before closing the database
 }
 
 // NewDB constructs a new DB and validates the schema
@@ -91,7 +90,7 @@ func NewDB(path string, metricsPrefix string) (db *DB, err error) {
 	db.configure(metricsPrefix)
 
 	// Create a quit channel for the periodic metrics collector and run it
-	db.quitChan = make(chan chan error)
+	db.quit = make(chan struct{})
 
 	go db.meter(10 * time.Second)
 
@@ -155,7 +154,7 @@ func (db *DB) WriteBatch(batch *leveldb.Batch) (err error) {
 
 // Close closes LevelDB database.
 func (db *DB) Close() (err error) {
-	close(db.quitChan)
+	close(db.quit)
 	return db.ldb.Close()
 }
 
@@ -186,18 +185,12 @@ func (db *DB) meter(refresh time.Duration) {
 		lastWritePaused time.Time
 	)
 
-	var (
-		errc chan error
-		merr error
-	)
-
 	// Iterate ad infinitum and collect the stats
-	for i := 1; errc == nil && merr == nil; i++ {
+	for i := 1; true; i++ {
 		// Retrieve the database stats
 		stats, err := db.ldb.GetProperty("leveldb.stats")
 		if err != nil {
 			log.Error("Failed to read database stats", "err", err)
-			merr = err
 			continue
 		}
 		// Find the compaction table, skip the header
@@ -207,7 +200,6 @@ func (db *DB) meter(refresh time.Duration) {
 		}
 		if len(lines) <= 3 {
 			log.Error("Compaction table not found")
-			merr = errors.New("compaction table not found")
 			continue
 		}
 		lines = lines[3:]
@@ -225,7 +217,6 @@ func (db *DB) meter(refresh time.Duration) {
 				value, err := strconv.ParseFloat(strings.TrimSpace(counter), 64)
 				if err != nil {
 					log.Error("Compaction entry parsing failed", "err", err)
-					merr = err
 					continue
 				}
 				compactions[i%2][idx] += value
@@ -246,7 +237,6 @@ func (db *DB) meter(refresh time.Duration) {
 		writedelay, err := db.ldb.GetProperty("leveldb.writedelay")
 		if err != nil {
 			log.Error("Failed to read database write delay statistic", "err", err)
-			merr = err
 			continue
 		}
 		var (
@@ -257,13 +247,11 @@ func (db *DB) meter(refresh time.Duration) {
 		)
 		if n, err := fmt.Sscanf(writedelay, "DelayN:%d Delay:%s Paused:%t", &delayN, &delayDuration, &paused); n != 3 || err != nil {
 			log.Error("Write delay statistic not found")
-			merr = err
 			continue
 		}
 		duration, err = time.ParseDuration(delayDuration)
 		if err != nil {
 			log.Error("Failed to parse delay duration", "err", err)
-			merr = err
 			continue
 		}
 		if db.writeDelayNMeter != nil {
@@ -285,24 +273,20 @@ func (db *DB) meter(refresh time.Duration) {
 		ioStats, err := db.ldb.GetProperty("leveldb.iostats")
 		if err != nil {
 			log.Error("Failed to read database iostats", "err", err)
-			merr = err
 			continue
 		}
 		var nRead, nWrite float64
 		parts := strings.Split(ioStats, " ")
 		if len(parts) < 2 {
 			log.Error("Bad syntax of ioStats", "ioStats", ioStats)
-			merr = fmt.Errorf("bad syntax of ioStats %s", ioStats)
 			continue
 		}
 		if n, err := fmt.Sscanf(parts[0], "Read(MB):%f", &nRead); n != 1 || err != nil {
 			log.Error("Bad syntax of read entry", "entry", parts[0])
-			merr = err
 			continue
 		}
 		if n, err := fmt.Sscanf(parts[1], "Write(MB):%f", &nWrite); n != 1 || err != nil {
 			log.Error("Bad syntax of write entry", "entry", parts[1])
-			merr = err
 			continue
 		}
 		if db.diskReadMeter != nil {
@@ -315,15 +299,11 @@ func (db *DB) meter(refresh time.Duration) {
 
 		// Sleep a bit, then repeat the stats collection
 		select {
-		case errc = <-db.quitChan:
+		case <-db.quit:
 			// Quit requesting, stop hammering the database
+			return
 		case <-time.After(refresh):
 			// Timeout, gather a new set of stats
 		}
 	}
-
-	if errc == nil {
-		errc = <-db.quitChan
-	}
-	errc <- merr
 }
```
