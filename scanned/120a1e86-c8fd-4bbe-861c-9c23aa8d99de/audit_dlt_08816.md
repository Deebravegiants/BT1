# [?] fix(relayer): prevent crawler block range underflow (#22075)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2026-08-31
Source: https://github.com/taikoxyz/taiko-mono/commit/f5543c71adfab1fa46397c94ca568afe83ae89f9
Type: security-commit

## Details
fix(relayer): prevent crawler block range underflow (#22075)

Co-authored-by: Claude Opus 5 <noreply@anthropic.com>

## Patch
### packages/relayer/indexer/indexer.go
```diff
@@ -370,16 +370,19 @@ func (i *Indexer) filter(ctx context.Context) error {
 				return errors.Wrap(err, "i.setInitialIndexingBlockByMode")
 			}
 
-			if i.latestIndexedBlockNumber < endBlockID-i.numLatestBlocksStartWhenCrawling {
-				i.latestIndexedBlockNumber = endBlockID - i.numLatestBlocksStartWhenCrawling
-			}
+			// both crawl windows are clamped to the history that actually exists.
+			// on a chain shorter than a configured window the unsigned subtraction
+			// would wrap to ~2^64 and the batch loop below would silently never run.
+			crawlStartBlockID := endBlockID - min(endBlockID, i.numLatestBlocksStartWhenCrawling)
 
-			if endBlockID > i.numLatestBlocksEndWhenCrawling {
-				// otherwise, we need to set the endBlockID as the greater of the two:
-				// either the endBlockID minus the number of latest blocks to ignore,
-				// or endBlockID.
-				endBlockID -= i.numLatestBlocksEndWhenCrawling
+			if i.latestIndexedBlockNumber < crawlStartBlockID {
+				i.latestIndexedBlockNumber = crawlStartBlockID
 			}
+
+			// ignore the latest N blocks from the end. when the chain is shorter than
+			// N, every block is still inside that window, so there is nothing mature
+			// enough to crawl yet and endBlockID clamps to 0.
+			endBlockID -= min(endBlockID, i.numLatestBlocksEndWhenCrawling)
 		}
 	}
 
```

### packages/relayer/indexer/indexer_test.go
```diff
@@ -9,6 +9,7 @@ import (
 
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/stretchr/testify/assert"
+	"github.com/stretchr/testify/require"
 	"github.com/taikoxyz/taiko-mono/packages/relayer"
 	"github.com/taikoxyz/taiko-mono/packages/relayer/bindings/bridge"
 	signalservice "github.com/taikoxyz/taiko-mono/packages/relayer/bindings/v4/signalservice"
@@ -51,6 +52,79 @@ func newTestService(syncMode SyncMode, watchMode WatchMode) (*Indexer, relayer.B
 	}, b
 }
 
+// filter dispatches on eventName, and this sentinel matches no case, which keeps
+// the test on the block-range arithmetic. The real event names cannot be used
+// here: newTestService leaves cfg nil and withRetry dereferences it.
+const noIndexedEventName = "no-event"
+
+func TestFilterCrawlPastBlocksClampsCrawlWindowsToAvailableHistory(t *testing.T) {
+	// mock.LatestBlockNumber is the source-chain head seen by filter.
+	head := mock.LatestBlockNumber.Uint64()
+
+	tests := []struct {
+		name       string
+		start      uint64
+		end        uint64
+		wantCursor uint64
+	}{
+		{
+			// the reported bug: the subtraction wrapped to ~2^64 and the crawler
+			// silently indexed nothing.
+			"start window longer than the chain",
+			50_400,
+			3,
+			head - 3,
+		},
+		{
+			"start window exactly the chain height",
+			head,
+			3,
+			head - 3,
+		},
+		{
+			"mature chain, both windows inside the history",
+			4,
+			1,
+			head - 1,
+		},
+		{
+			// production defaults on a chain shorter than the end window: every
+			// block is still unripe, so the crawler must index nothing rather
+			// than run past its own exclusion window.
+			"end window longer than the chain",
+			50_400,
+			300,
+			0,
+		},
+		{
+			"end window exactly the chain height",
+			50_400,
+			head,
+			0,
+		},
+		{
+			"no windows configured",
+			0,
+			0,
+			head,
+		},
+	}
+
+	for _, tt := range tests {
+		t.Run(tt.name, func(t *testing.T) {
+			i, _ := newTestService(Resync, CrawlPastBlocks)
+			i.eventName = noIndexedEventName
+			i.numLatestBlocksStartWhenCrawling = tt.start
+			i.numLatestBlocksEndWhenCrawling = tt.end
+
+			err := i.filter(context.Background())
+
+			require.NoError(t, err)
+			assert.Equal(t, tt.wantCursor, i.latestIndexedBlockNumber)
+		})
+	}
+}
+
 func TestHandleMessageProcessedEventSkipsIgnoredMessageHash(t *testing.T) {
 	ignoredHash := common.HexToHash("0x0000000000000000000000000000000000000000000000000000000000000001")
 	i, b := newTestService(Sync, Filter)
```
