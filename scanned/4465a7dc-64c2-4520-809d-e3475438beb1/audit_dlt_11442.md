# [?] [fix] Fix engine panic when we get a zero response (#12890)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2024-04-19
Source: https://github.com/smartcontractkit/ccip/commit/facaf9a86085b709efb66cde5bedd69857310ed0
Type: security-commit

## Details
[fix] Fix engine panic when we get a zero response (#12890)

## Patch
### core/services/workflows/engine.go
```diff
@@ -219,7 +219,12 @@ func (e *Engine) loop(ctx context.Context) {
 		case <-ctx.Done():
 			e.logger.Debugw("shutting down loop")
 			return
-		case resp := <-e.triggerEvents:
+		case resp, isOpen := <-e.triggerEvents:
+			if !isOpen {
+				e.logger.Errorf("trigger events channel is no longer open, skipping")
+				continue
+			}
+
 			if resp.Err != nil {
 				e.logger.Errorf("trigger event was an error; not executing", resp.Err)
 				continue
```
