# [?] fix blockchain index builder data race (#514)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2019-02-05
Source: https://github.com/iotexproject/iotex-core/commit/0b3c83fad7eb0c63685824869c6e271e6dd18fc8
Type: security-commit

## Details
fix blockchain index builder data race (#514)

## Patch
### blockchain/indexbuilder.go
```diff
@@ -40,6 +40,7 @@ func init() {
 type IndexBuilder struct {
 	store        db.KVStore
 	pendingBlks  chan *block.Block
+	cancelChan   chan interface{}
 	timerFactory *prometheustimer.TimerFactory
 }
 
@@ -61,48 +62,54 @@ func NewIndexBuilder(chain Blockchain) (*IndexBuilder, error) {
 	return &IndexBuilder{
 		store:        bc.dao.kvstore,
 		pendingBlks:  make(chan *block.Block, 64), // Actually 1 should be enough
+		cancelChan:   make(chan interface{}),
 		timerFactory: timerFactory,
 	}, nil
 }
 
 // Start starts the index builder
 func (ib *IndexBuilder) Start(_ context.Context) error {
 	go func() {
-		for blk := range ib.pendingBlks {
-			timer := ib.timerFactory.NewTimer("indexBlock")
-			batch := db.NewBatch()
-			if err := indexBlock(ib.store, blk, batch); err != nil {
-				log.L().Info(
-					"Error when indexing the block",
-					zap.Uint64("height", blk.Height()),
-					zap.Error(err),
-				)
+		for {
+			select {
+			case <-ib.cancelChan:
+				return
+			case blk := <-ib.pendingBlks:
+				timer := ib.timerFactory.NewTimer("indexBlock")
+				batch := db.NewBatch()
+				if err := indexBlock(ib.store, blk, batch); err != nil {
+					log.L().Info(
+						"Error when indexing the block",
+						zap.Uint64("height", blk.Height()),
+						zap.Error(err),
+					)
+				}
+				// index receipts
+				if err := putReceipts(blk.Height(), blk.Receipts, batch); err != nil {
+					log.L().Info(
+						"Error when indexing the block",
+						zap.Uint64("height", blk.Height()),
+						zap.Error(err),
+					)
+				}
+				batchSizeMtc.WithLabelValues().Set(float64(batch.Size()))
+				if err := ib.store.Commit(batch); err != nil {
+					log.L().Info(
+						"Error when indexing the block",
+						zap.Uint64("height", blk.Height()),
+						zap.Error(err),
+					)
+				}
+				timer.End()
 			}
-			// index receipts
-			if err := putReceipts(blk.Height(), blk.Receipts, batch); err != nil {
-				log.L().Info(
-					"Error when indexing the block",
-					zap.Uint64("height", blk.Height()),
-					zap.Error(err),
-				)
-			}
-			batchSizeMtc.WithLabelValues().Set(float64(batch.Size()))
-			if err := ib.store.Commit(batch); err != nil {
-				log.L().Info(
-					"Error when indexing the block",
-					zap.Uint64("height", blk.Height()),
-					zap.Error(err),
-				)
-			}
-			timer.End()
 		}
 	}()
 	return nil
 }
 
 // Stop stops the index builder
 func (ib *IndexBuilder) Stop(_ context.Context) error {
-	close(ib.pendingBlks)
+	close(ib.cancelChan)
 	return nil
 }
 
```
