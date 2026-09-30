# [?] Fix data race in timeboost_test.go

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-03-26
Source: https://github.com/OffchainLabs/nitro/commit/2b81eb15d6366b07e368f3f7fbd7251c2c8d2d64
Type: security-commit

## Details
Fix data race in timeboost_test.go

## Patch
### system_tests/timeboost_test.go
```diff
@@ -1663,7 +1663,6 @@ func setupExpressLaneAuction(
 
 	// This is hacky- we are manually starting the ExpressLaneService here instead of letting it be started
 	// by the sequencer. This is due to needing to deploy the auction contract first.
-	builderSeq.execConfig.Sequencer.Dangerous.Timeboost.Enable = true
 	roundTimingInfo, err := gethexec.GetRoundTimingInfo(auctionContract)
 	Require(t, err)
 
@@ -1698,6 +1697,7 @@ func setupExpressLaneAuction(
 	}
 
 	expressLaneTracker.Start(ctx)
+	builderSeq.execConfig.Sequencer.Dangerous.Timeboost.Enable = true // Prevents race in sequencer where expressLaneService is read inside publishTransactionToQueue
 
 	// Set up an autonomous auction contract service that runs in the background in this test.
 	redisURL := redisutil.CreateTestRedis(ctx, t)
```
