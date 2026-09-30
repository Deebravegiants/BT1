# [?] Fix flaky tests: timing and race condition (#10455)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-02-08
Source: https://github.com/NethermindEth/nethermind/commit/129fcbfe72e7affdbb7734e66fcd8abcb9975413
Type: security-commit

## Details
Fix flaky tests: timing and race condition (#10455)

- PeerManagerTests: Increase After timeout from 1000ms to 3000ms in
  Will_not_stop_trying_on_rlpx_connection_failure to prevent false
  failures on loaded CI runners
- SyncServerTests: Use Interlocked.Increment in
  Broadcast_NewBlock_on_arrival_to_sqrt_of_peers to fix race condition
  where concurrent SyncPeerMock background threads could lose count
  increments
- Rename _travisDelay fields to _delay, _delayLong, _delayLonger

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### src/Nethermind/Nethermind.Network.Test/PeerManagerTests.cs
```diff
@@ -78,7 +78,7 @@ public async Task Will_connect_to_a_candidate_node()
             ctx.SetupPersistedPeers(1);
             ctx.PeerPool.Start();
             ctx.PeerManager.Start();
-            Assert.That(() => ctx.RlpxPeer.ConnectAsyncCallsCount, Is.EqualTo(1).After(_travisDelay, 10));
+            Assert.That(() => ctx.RlpxPeer.ConnectAsyncCallsCount, Is.EqualTo(1).After(_delay, 10));
         }
 
         [Test, Retry(3)]
@@ -88,14 +88,14 @@ public async Task Will_only_connect_up_to_max_peers()
             ctx.SetupPersistedPeers(50);
             ctx.PeerPool.Start();
             ctx.PeerManager.Start();
-            await Task.Delay(_travisDelayLong);
+            await Task.Delay(_delayLong);
 
             int expectedConnectCount = 25;
             Assert.That(
                 () => ctx.RlpxPeer.ConnectAsyncCallsCount,
                 Is
                     .InRange(expectedConnectCount, expectedConnectCount + 1)
-                    .After(_travisDelay * 10, 10));
+                    .After(_delay * 10, 10));
         }
 
         [Test]
@@ -256,11 +256,11 @@ public async Task Will_fill_up_on_disconnects()
             ctx.SetupPersistedPeers(50);
             ctx.PeerPool.Start();
             ctx.PeerManager.Start();
-            await Task.Delay(_travisDelayLong);
+            await Task.Delay(_delayLong);
             Assert.That(ctx.RlpxPeer.ConnectAsyncCallsCount, Is.AtLeast(25));
             ctx.DisconnectAllSessions();
 
-            await Task.Delay(_travisDelayLong);
+            await Task.Delay(_delayLong);
             Assert.That(ctx.RlpxPeer.ConnectAsyncCallsCount, Is.AtLeast(50));
         }
 
@@ -273,7 +273,7 @@ public async Task Ok_if_fails_to_connect()
             ctx.PeerPool.Start();
             ctx.PeerManager.Start();
 
-            Assert.That(() => ctx.PeerManager.ActivePeers.Count, Is.EqualTo(0).After(_travisDelay, 10));
+            Assert.That(() => ctx.PeerManager.ActivePeers.Count, Is.EqualTo(0).After(_delay, 10));
         }
 
         [Test, Retry(3)]
@@ -296,7 +296,7 @@ public async Task Will_fill_up_over_and_over_again_on_disconnects()
                 {
                     Assert.That(
                         () => ctx.PeerPool.ActivePeers.Count,
-                        Is.AtLeast(25).After(_travisDelayLonger * 2, 10));
+                        Is.AtLeast(25).After(_delayLonger * 2, 10));
                     ctx.DisconnectAllSessions();
                 }
             }
@@ -318,7 +318,7 @@ public async Task Will_fill_up_over_and_over_again_on_newly_discovered()
             for (int i = 0; i < 10; i++)
             {
                 ctx.DiscoverNew(25);
-                Assert.That(() => ctx.PeerManager.ActivePeers.Count, Is.EqualTo(25).After(_travisDelay, 10));
+                Assert.That(() => ctx.PeerManager.ActivePeers.Count, Is.EqualTo(25).After(_delay, 10));
             }
         }
 
@@ -334,8 +334,8 @@ public async Task Will_not_stop_trying_on_rlpx_connection_failure()
             for (int i = 0; i < 10; i++)
             {
                 ctx.DiscoverNew(25);
-                await Task.Delay(_travisDelay);
-                Assert.That(() => ctx.RlpxPeer.ConnectAsyncCallsCount, Is.EqualTo(25 * (i + 1)).After(1000, 10));
+                await Task.Delay(_delay);
+                Assert.That(() => ctx.RlpxPeer.ConnectAsyncCallsCount, Is.EqualTo(25 * (i + 1)).After(_delayLonger, 10));
             }
         }
 
@@ -377,13 +377,13 @@ public async Task IfPeerAdded_with_invalid_chain_then_do_not_connect()
 
             ctx.PeerPool.GetOrAdd(networkNode);
 
-            Assert.That(() => ctx.PeerPool.ActivePeers.Count, Is.EqualTo(0).After(_travisDelay, 10));
+            Assert.That(() => ctx.PeerPool.ActivePeers.Count, Is.EqualTo(0).After(_delay, 10));
         }
 
-        private readonly int _travisDelay = 500;
+        private readonly int _delay = 500;
 
-        private readonly int _travisDelayLong = 1000;
-        private readonly int _travisDelayLonger = 3000;
+        private readonly int _delayLong = 1000;
+        private readonly int _delayLonger = 3000;
 
         [Test]
         [Ignore("Behaviour changed that allows peers to go over max if awaiting response")]
@@ -397,7 +397,7 @@ public async Task Will_fill_up_with_incoming_over_and_over_again_on_disconnects(
             for (int i = 0; i < 10; i++)
             {
                 ctx.CreateNewIncomingSessions(25);
-                Assert.That(() => ctx.PeerManager.ActivePeers.Count, Is.EqualTo(25).After(_travisDelay, 10));
+                Assert.That(() => ctx.PeerManager.ActivePeers.Count, Is.EqualTo(25).After(_delay, 10));
             }
         }
 
@@ -416,10 +416,10 @@ public async Task Will_fill_up_over_and_over_again_on_disconnects_and_when_ids_k
             {
                 currentCount += 25;
                 maxCount += 50;
-                Assert.That(() => ctx.RlpxPeer.ConnectAsyncCallsCount, Is.InRange(currentCount, maxCount).After(_travisDelayLonger * 2, 10));
+                Assert.That(() => ctx.RlpxPeer.ConnectAsyncCallsCount, Is.InRange(currentCount, maxCount).After(_delayLonger * 2, 10));
                 ctx.RlpxPeer.ConnectAsyncCallsCount.Should().BeInRange(currentCount, maxCount);
                 ctx.HandshakeAllSessions();
-                await Task.Delay(_travisDelay);
+                await Task.Delay(_delay);
                 ctx.DisconnectAllSessions();
             }
 
@@ -448,10 +448,10 @@ public async Task Will_fill_up_over_and_over_again_on_disconnects_and_when_ids_k
             for (int i = 0; i < 10; i++)
             {
                 currentCount += count;
-                await Task.Delay(_travisDelayLong);
+                await Task.Delay(_delayLong);
                 ctx.RlpxPeer.ConnectAsyncCallsCount.Should().BeInRange(currentCount, currentCount + count);
                 ctx.HandshakeAllSessions();
-                await Task.Delay(_travisDelay);
+                await Task.Delay(_delay);
                 ctx.DisconnectAllSessions();
             }
         }
@@ -473,12 +473,12 @@ public async Task Will_fill_up_over_and_over_again_on_disconnects_and_when_ids_k
             for (int i = 0; i < 10; i++)
             {
                 currentCount += count;
-                await Task.Delay(_travisDelayLong);
+                await Task.Delay(_delayLong);
                 ctx.RlpxPeer.ConnectAsyncCallsCount.Should().BeInRange(currentCount, currentCount + count);
                 ctx.HandshakeAllSessions();
-                await Task.Delay(_travisDelay);
+                await Task.Delay(_delay);
                 ctx.CreateIncomingSessions();
-                await Task.Delay(_travisDelay);
+                await Task.Delay(_delay);
                 ctx.DisconnectAllSessions();
             }
         }
@@ -514,7 +514,7 @@ public async Task Will_load_static_nodes_and_connect_to_them()
                 ctx.TestNodeSource.AddNode(new Node(TestItem.PublicKeyA, node.Host, node.Port));
             }
 
-            Assert.That(() => ctx.PeerManager.ActivePeers.Count(static p => p.Node.IsStatic), Is.EqualTo(nodesCount).After(_travisDelay, 10));
+            Assert.That(() => ctx.PeerManager.ActivePeers.Count(static p => p.Node.IsStatic), Is.EqualTo(nodesCount).After(_delay, 10));
         }
 
         [Test, Retry(5)]
@@ -527,7 +527,7 @@ public async Task Will_disconnect_on_remove_static_node()
             ctx.StaticNodesManager.DiscoverNodes(Arg.Any<CancellationToken>()).Returns(staticNodes.Select(n => new Node(n, true)).ToAsyncEnumerable());
             ctx.PeerPool.Start();
             ctx.PeerManager.Start();
-            await Task.Delay(_travisDelay);
+            await Task.Delay(_delay);
 
             void DisconnectHandler(object o, DisconnectEventArgs e) => disconnections++;
             ctx.Sessions.ForEach(s => s.Disconnected += DisconnectHandler);
@@ -548,7 +548,7 @@ public async Task Will_connect_and_disconnect_on_peer_management()
             ctx.PeerManager.Start();
             var node = new NetworkNode(ctx.GenerateEnode());
             ctx.PeerPool.GetOrAdd(node);
-            await Task.Delay(_travisDelayLong);
+            await Task.Delay(_delayLong);
 
             void DisconnectHandler(object o, DisconnectEventArgs e) => disconnections++;
             ctx.PeerManager.ActivePeers.Select(p => p.Node.Id).Should().BeEquivalentTo(new[] { node.NodeId });
@@ -570,7 +570,7 @@ public async Task Will_only_add_same_peer_once()
             ctx.PeerPool.GetOrAdd(node);
             ctx.PeerPool.GetOrAdd(node);
             ctx.PeerPool.GetOrAdd(node);
-            await Task.Delay(_travisDelayLong);
+            await Task.Delay(_delayLong);
             ctx.PeerManager.ActivePeers.Should().HaveCount(1);
         }
 
@@ -581,7 +581,7 @@ public async Task RemovePeer_should_fail_if_peer_not_added()
             ctx.PeerPool.Start();
             ctx.PeerManager.Start();
             var node = new NetworkNode(ctx.GenerateEnode());
-            Assert.That(() => ctx.PeerPool.TryRemove(node.NodeId, out _), Is.False.After(_travisDelay, 10));
+            Assert.That(() => ctx.PeerPool.TryRemove(node.NodeId, out _), Is.False.After(_delay, 10));
         }
 
         private class Context : IAsyncDisposable
```

### src/Nethermind/Nethermind.Synchronization.Test/SyncServerTests.cs
```diff
@@ -666,7 +666,7 @@ public async Task Broadcast_NewBlock_on_arrival_to_sqrt_of_peers([Values(1, 2, 3
         int count = 0;
         remoteServer
             .When(r => r.AddNewBlock(Arg.Is<Block>(b => b.Hash == remoteBlockTree.Head!.Hash), Arg.Any<ISyncPeer>()))
-            .Do(_ => count++);
+            .Do(_ => Interlocked.Increment(ref count));
         PeerInfo[] peers = Enumerable.Range(0, peerCount).Take(peerCount)
             .Select(_ => new PeerInfo(new SyncPeerMock(remoteBlockTree, remoteSyncServer: remoteServer)))
             .ToArray();
```
