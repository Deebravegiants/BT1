# [?] Fix broadcast client shutdown deadlock (#3882)

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-10-20
Source: https://github.com/OffchainLabs/nitro/commit/e9bddea5ef738d0dfae482becffedb4e8b1974e7
Type: security-commit

## Details
Fix broadcast client shutdown deadlock (#3882)

Add context-aware escape hatches to channel sends in broadcast client
to prevent goroutines from blocking indefinitely during shutdown. When
the context is cancelled, goroutines can now exit cleanly instead of
waiting forever on full channel buffers that will never be drained.

## Patch
### broadcastclient/broadcastclient.go
```diff
@@ -196,7 +196,10 @@ func (bc *BroadcastClient) Start(ctxIn context.Context) {
 				errors.Is(err, ErrIncorrectChainId) ||
 				errors.Is(err, ErrMissingFeedServerVersion) ||
 				errors.Is(err, ErrIncorrectFeedServerVersion) {
-				bc.fatalErrChan <- fmt.Errorf("failed connecting to server feed due to %w", err)
+				select {
+				case bc.fatalErrChan <- fmt.Errorf("failed connecting to server feed due to %w", err):
+				case <-ctx.Done():
+				}
 				return
 			}
 			if err == nil {
@@ -491,7 +494,11 @@ func (bc *BroadcastClient) startBackgroundReader(earlyFrameData io.Reader) {
 						}
 					}
 					if res.ConfirmedSequenceNumberMessage != nil && bc.confirmedSequenceNumberListener != nil {
-						bc.confirmedSequenceNumberListener <- res.ConfirmedSequenceNumberMessage.SequenceNumber
+						select {
+						case bc.confirmedSequenceNumberListener <- res.ConfirmedSequenceNumberMessage.SequenceNumber:
+						case <-ctx.Done():
+							return
+						}
 					}
 				}
 			}
```
