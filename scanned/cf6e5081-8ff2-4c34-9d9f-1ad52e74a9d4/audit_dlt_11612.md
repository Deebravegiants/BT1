# [?] fix(deploy tool): Do not crash on unknown events

## Summary
Severity: Unknown
Chain: Akash
Component: akash-network/node
Published: 2021-02-24
Source: https://github.com/akash-network/node/commit/3bde5ee9b9f5fef70b1228bcb368de4c17567e21
Type: security-commit

## Details
fix(deploy tool): Do not crash on unknown events

## Patch
### deploy/cmd/event-handlers.go
```diff
@@ -170,9 +170,10 @@ func DeploymentDataUpdateHandler(dd *DeploymentData, bids chan<- mtypes.EventBid
 			}
 			return
 
-		// In any other case we should exit with error
+		// Ignore any other event
 		default:
-			return fmt.Errorf("%w: %T", errUnexpectedEvent, ev)
+			log.Debug("Ignoring event")
+			return
 		}
 	}
 }
```
