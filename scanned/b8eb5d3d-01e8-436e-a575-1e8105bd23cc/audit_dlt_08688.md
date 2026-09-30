# [?] fix deadlock in execution engine

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-04-14
Source: https://github.com/OffchainLabs/nitro/commit/50557e9066eee9bb386804a9e722710936050dd1
Type: security-commit

## Details
fix deadlock in execution engine

## Patch
### execution/gethexec/executionengine.go
```diff
@@ -497,8 +497,15 @@ func (s *ExecutionEngine) Reorg(msgIdxOfFirstMsgToAdd arbutil.MessageIndex, newM
 		s.recorder.ReorgTo(lastBlockToKeep.Header())
 	}
 	if len(oldMessages) > 0 {
-		s.resequenceChan <- oldMessages
-		resequencing = true
+		// Use a select to avoid blocking forever if the resequence goroutine
+		// has already exited (e.g., because the context was cancelled during
+		// shutdown before the nodes were stopped).
+		select {
+		case s.resequenceChan <- oldMessages:
+			resequencing = true
+		case <-s.GetContext().Done():
+			log.Warn("ExecutionEngine: context cancelled, skipping message resequencing")
+		}
 	}
 	return newMessagesResults, nil
 }
```
