# [?] mitigated race condition between FundingLocked and AnnouncementSignatures

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2017-02-23
Source: https://github.com/ACINQ/eclair/commit/a33d5ef1a05c76273f23a5008532ec163599aa2b
Type: security-commit

## Details
mitigated race condition between FundingLocked and AnnouncementSignatures

## Patch
### eclair-node/src/main/scala/fr/acinq/eclair/channel/Channel.scala
```diff
@@ -302,8 +302,9 @@ class Channel(val r: ActorRef, val blockchain: ActorRef, router: ActorRef, relay
       blockchain ! WatchLost(self, commitments.anchorId, params.minimumDepth, BITCOIN_FUNDING_LOST)
       val nextPerCommitmentPoint = Generators.perCommitPoint(params.localParams.shaSeed, 1)
       val fundingLocked = FundingLocked(temporaryChannelId, channelId, nextPerCommitmentPoint)
-      remote ! fundingLocked
       deferred.map(self ! _)
+      remote ! fundingLocked
+      log.info(s"unstashing messages")
       // TODO: htlcIdx should not be 0 when resuming connection
       goto(WAIT_FOR_FUNDING_LOCKED) using DATA_WAIT_FOR_FUNDING_LOCKED(params, commitments.copy(channelId = channelId), fundingLocked)
 
```
