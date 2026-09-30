# [?] lnpeer: chan_reest: ctn overflow: force-close instead of disconnect

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2026-08-05
Source: https://github.com/spesmilo/electrum/commit/b3e441f861899f8d09968608e1e2439152b043f1
Type: security-commit

## Details
lnpeer: chan_reest: ctn overflow: force-close instead of disconnect

(was DC-ing due to assert failing in RevocationStore)

also add a test case

## Patch
### electrum/lnpeer.py
```diff
@@ -1529,6 +1529,11 @@ async def on_channel_reestablish(self, chan: Channel, msg):
         # sanity checks of received values
         assert their_next_local_ctn >= 0  # already done by lnmsg, as type is u64
         assert their_oldest_unrevoked_remote_ctn >= 0
+        if max(their_next_local_ctn, their_oldest_unrevoked_remote_ctn) >= 2**48:
+            # TODO: upstream this check to lightning/bolts spec
+            self.logger.error(f"channel_reestablish ({chan.get_id_for_log()}): ctn overflow")
+            self.schedule_force_closing(chan.channel_id)
+            raise RemoteMisbehaving("channel_reestablish: ctn overflow")
         # ctns
         oldest_unrevoked_local_ctn = chan.get_oldest_unrevoked_ctn(LOCAL)
         latest_remote_ctn = chan.get_latest_ctn(REMOTE)
```

### tests/test_lnpeer.py
```diff
@@ -253,7 +253,7 @@ def prepare_peers(
         w1, w2 = graph.workers.values()
         return p1, p2, w1, w2
 
-    async def test_reestablish(self):
+    async def test_reestablish_happycase(self):
         graph = self.prepare_chans_and_peers_in_graph(self.GRAPH_DEFINITIONS['single_chan'])
         p1, p2 = graph.peers.values()
         alice_channel = graph.channels[('alice', 'bob')][0]
@@ -267,6 +267,7 @@ async def reestablish():
                 p2.reestablish_channel(bob_channel))
             self.assertEqual(alice_channel.peer_state, PeerState.GOOD)
             self.assertEqual(bob_channel.peer_state, PeerState.GOOD)
+            self.assertEqual((alice_channel._state, bob_channel._state), (ChannelState.OPEN, ChannelState.OPEN))
             gath.cancel()
         gath = asyncio.gather(reestablish(), p1._message_loop(), p2._message_loop(), p1.htlc_switch(), p2.htlc_switch())
         with self.assertRaises(asyncio.CancelledError):
@@ -354,10 +355,11 @@ async def alice_sends_reest():
                 oldest_unrevoked_remote_ctn = chan.get_oldest_unrevoked_ctn(REMOTE) + revnum_delta
                 assert oldest_unrevoked_remote_ctn >= 0, oldest_unrevoked_remote_ctn
                 if last_rev_secret is None:
+                    revnum_for_secret = oldest_unrevoked_remote_ctn % (2**48)
                     if revnum_delta <= 0:
-                        last_rev_secret = chan.revocation_store.retrieve_secret(RevocationStore.START_INDEX - oldest_unrevoked_remote_ctn + 1)
+                        last_rev_secret = chan.revocation_store.retrieve_secret(RevocationStore.START_INDEX - revnum_for_secret + 1)
                     else:  # Alice is using *magic* here, i.e. cheating: she uses Bob's channel to learn future unrevealed secrets
-                        last_rev_secret, _point = bob_channel.get_secret_and_point(LOCAL, oldest_unrevoked_remote_ctn - 1)
+                        last_rev_secret, _point = bob_channel.get_secret_and_point(LOCAL, revnum_for_secret - 1)
                 p1.send_message(
                     "channel_reestablish",
                     channel_id=chan.channel_id,
@@ -411,6 +413,18 @@ async def exit_after_bob_receives_reest():
             with self.subTest(msg="invalid last_rev_secret", **kwargs):
                 a_chan, b_chan = await f(last_rev_secret=sha256("fake_data"), **kwargs)
                 self.assertEqual((a_chan._state, b_chan._state), (cs.OPEN, cs.FORCE_CLOSING))
+            with self.subTest(msg="overflow of next_local_ctn", **kwargs):
+                with self.assertLogs('electrum', level='INFO') as logs:
+                    a_chan, b_chan = await f(ctn_delta=2**48, **kwargs)
+                self.assertEqual((a_chan._state, b_chan._state), (cs.OPEN, cs.FORCE_CLOSING))
+                self.assertTrue(any(("bob->alice" in msg and "channel_reestablish" in msg and "ctn overflow" in msg)
+                                    for msg in logs.output))
+            with self.subTest(msg="overflow of oldest_unrevoked_remote_ctn", **kwargs):
+                with self.assertLogs('electrum', level='INFO') as logs:
+                    a_chan, b_chan = await f(revnum_delta=2**48, **kwargs)
+                self.assertEqual((a_chan._state, b_chan._state), (cs.OPEN, cs.FORCE_CLOSING))
+                self.assertTrue(any(("bob->alice" in msg and "channel_reestablish" in msg and "ctn overflow" in msg)
+                                    for msg in logs.output))
 
     @staticmethod
     def _send_fake_htlc(peer: Peer, chan: Channel) -> UpdateAddHtlc:
```
