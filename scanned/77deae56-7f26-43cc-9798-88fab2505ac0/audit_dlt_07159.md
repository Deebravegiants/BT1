# [?] discovery: fix log line panic

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-06-30
Source: https://github.com/lightningnetwork/lnd/commit/25daf253c0f64955d9b840dbd5f63b599aead1d3
Type: security-commit

## Details
discovery: fix log line panic

If a method returns an error, we should assume all other parameters to
be nil unless the documentation explicitly says otherwise. So here, we
fix a log line where a dereference is made to an object that will be nil
due to an error being returned.

## Patch
### discovery/gossiper.go
```diff
@@ -2236,7 +2236,7 @@ func (d *AuthenticatedGossiper) isMsgStale(_ context.Context,
 		}
 		if err != nil {
 			log.Debugf("Unable to retrieve channel=%v from graph: "+
-				"%v", chanInfo.ChannelID, err)
+				"%v", msg.ShortChannelID, err)
 			return false
 		}
 
```
