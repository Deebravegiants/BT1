# [?] htlcswitch: fix hodlQueue deadlock by stopping htlcManager first

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2026-04-07
Source: https://github.com/lightningnetwork/lnd/commit/f550ac1f7c6416c3f45e253f0ec9e0df86f387fb
Type: security-commit

## Details
htlcswitch: fix hodlQueue deadlock by stopping htlcManager first

The channelLink.Stop() teardown had an inverted ordering that could
cause a permanent deadlock of the invoice registry under concurrent
peer disconnect.

The previous order was:
  1. HodlUnsubscribeAll  -- removes subscriptions
  2. hodlQueue.Stop()    -- kills the queue's internal goroutine
  3. cg.Quit()           -- signals htlcManager to stop
  4. cg.WgWait()         -- waits for htlcManager to exit

The race window between steps 2 and 4 left htlcManager alive. A
RevokeAndAck arriving during that window could drive processRemoteAdds
→ processExitHop → NotifyExitHopHtlc, registering a new hodl
subscription backed by a dead hodlQueue (ChanIn() has no reader).

Any subsequent call to notifyHodlSubscribers (e.g. MPP auto-release
timer, expiry watcher, or explicit settle/cancel) would then block
indefinitely on the unbuffered ChanIn(), holding hodlSubscriptionsMux.
Concurrent NotifyExitHopHtlc calls waiting for that lock, plus callers
holding the invoice-level lock waiting for those, produce a full
deadlock of the invoice registry with no recovery path short of a
daemon restart.

The fix is to stop htlcManager before touching the hodl subscription
state. htlcManager is the sole caller of NotifyExitHopHtlc, so once
cg.WgWait() returns no new subscriptions can be registered, making
HodlUnsubscribeAll and hodlQueue.Stop() race-free.

## Patch
### htlcswitch/link.go
```diff
@@ -629,8 +629,20 @@ func (l *channelLink) Stop() {
 
 	l.log.Info("stopping")
 
-	// As the link is stopping, we are no longer interested in htlc
-	// resolutions coming from the invoice registry.
+	// Stop the htlcManager goroutine first. This is critical: htlcManager
+	// is the sole caller of NotifyExitHopHtlc, which registers new hodl
+	// subscriptions. We must guarantee it has fully exited before we
+	// remove subscriptions and stop the hodlQueue. Without this ordering,
+	// a RevokeAndAck processed in the race window between hodlQueue.Stop()
+	// and cg.Quit() can register an orphaned subscription against a dead
+	// queue, causing notifyHodlSubscribers to block permanently and
+	// deadlock the entire invoice registry.
+	l.cg.Quit()
+	l.cg.WgWait()
+
+	// htlcManager has fully exited — no new hodl subscriptions can be
+	// registered from this point on. It is now safe to remove all
+	// subscriptions and tear down the queue.
 	l.cfg.Registry.HodlUnsubscribeAll(l.hodlQueue.ChanIn())
 
 	if l.cfg.ChainEvents.Cancel != nil {
@@ -651,9 +663,6 @@ func (l *channelLink) Stop() {
 		l.hodlQueue.Stop()
 	}
 
-	l.cg.Quit()
-	l.cg.WgWait()
-
 	// Now that the htlcManager has completely exited, reset the packet
 	// courier. This allows the mailbox to revaluate any lingering Adds that
 	// were delivered but didn't make it on a commitment to be failed back
```
