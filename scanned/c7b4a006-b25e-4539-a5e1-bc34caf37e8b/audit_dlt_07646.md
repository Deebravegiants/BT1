# [?] Resolve some discovery dos vectors(which hive revealed) (#12211)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-07-07
Source: https://github.com/NethermindEth/nethermind/commit/f905eb2ac41520e49c88729939bcbe5f7b0d59b8
Type: security-commit

## Details
Resolve some discovery dos vectors(which hive revealed) (#12211)

## Patch
### src/Nethermind/Nethermind.Network.Discovery.Test/DiscoveryV5AppTests.cs
```diff
@@ -367,4 +367,24 @@ public void Should_Use_Discovery_Port_From_Configured_Enode_Bootnode()
             Assert.That(bootNodes[0].Host, Is.EqualTo("8.8.8.8"));
         }
     }
+
+    [TestCase("8.8.8.8", true, true)]
+    [TestCase("8.8.8.8", false, false)]
+    [TestCase("127.0.0.1", true, false)]
+    [TestCase("192.168.0.1", true, false)]
+    [TestCase("169.254.0.1", true, false)]
+    [TestCase("0.0.0.0", true, true)]
+    [TestCase("::", true, true)]
+    [TestCase("255.255.255.255", true, true)]
+    public void Should_Use_Default_Discv5_Bootnodes_Unless_Disabled_Or_Address_Is_Known_Private(string externalIp, bool configured, bool expected)
+    {
+        DiscoveryConfig discoveryConfig = new()
+        {
+            UseDefaultDiscv5Bootnodes = configured
+        };
+
+        bool result = DiscoveryV5App.ShouldUseDefaultDiscv5Bootnodes(IPAddress.Parse(externalIp), discoveryConfig);
+
+        Assert.That(result, Is.EqualTo(expected));
+    }
 }
```

### src/Nethermind/Nethermind.Network.Discovery.Test/Discv4/EndpointBondTableTests.cs
```diff
@@ -0,0 +1,213 @@
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
+// SPDX-License-Identifier: LGPL-3.0-only
+
+using System.Net;
+using Nethermind.Network.Discovery.Discv4;
+using NUnit.Framework;
+
+namespace Nethermind.Network.Discovery.Test.Discv4
+{
+    [Parallelizable(ParallelScope.All)]
+    [TestFixture]
+    public class EndpointBondTableTests
+    {
+        private static EndpointKey Endpoint(int port) => new(new IPEndPoint(IPAddress.Loopback, port));
+
+        [Test]
+        public void Default_table_is_empty()
+        {
+            EndpointBondTable table = default;
+
+            Assert.That(table.IsEmpty, Is.True);
+            Assert.That(table.Count, Is.EqualTo(0));
+            Assert.That(table.Contains(Endpoint(1)), Is.False);
+            Assert.That(table.HasFresh(Endpoint(1), 0), Is.False);
+        }
+
+        [Test]
+        public void Operations_on_empty_table_do_not_throw_or_change_state()
+        {
+            EndpointBondTable table = default;
+
+            Assert.That(table.Remove(Endpoint(1), 123), Is.False);
+            Assert.DoesNotThrow(() => table.PruneStale(long.MaxValue));
+            Assert.That(table.IsEmpty, Is.True);
+        }
+
+        [Test]
+        public void Record_adds_new_endpoint()
+        {
+            EndpointBondTable table = default;
+
+            Assert.That(table.Record(Endpoint(1), stamp: 10), Is.False);
+
+            Assert.That(table.IsEmpty, Is.False);
+            Assert.That(table.Count, Is.EqualTo(1));
+            Assert.That(table.Contains(Endpoint(1)), Is.True);
+        }
+
+        [Test]
+        public void Record_refreshes_existing_endpoint_without_growing()
+        {
+            EndpointBondTable table = default;
+            table.Record(Endpoint(1), stamp: 10);
+
+            Assert.That(table.Record(Endpoint(1), stamp: 20), Is.False);
+
+            Assert.That(table.Count, Is.EqualTo(1));
+            Assert.That(table.HasFresh(Endpoint(1), minValidStamp: 15), Is.True, "should reflect the refreshed stamp");
+        }
+
+        [Test]
+        public void Endpoints_differ_by_address_and_port()
+        {
+            EndpointKey a = new(IPAddress.Parse("10.0.0.1"), 30303);
+            EndpointKey samePortDifferentAddress = new(IPAddress.Parse("10.0.0.2"), 30303);
+            EndpointKey sameAddressDifferentPort = new(IPAddress.Parse("10.0.0.1"), 30304);
+
+            EndpointBondTable table = default;
+            table.Record(a, stamp: 1);
+
+            Assert.That(table.Contains(a), Is.True);
+            Assert.That(table.Contains(samePortDifferentAddress), Is.False);
+            Assert.That(table.Contains(sameAddressDifferentPort), Is.False);
+            Assert.That(table.Count, Is.EqualTo(1));
+        }
+
+        [TestCase(9L, true)]
+        [TestCase(10L, false)]
+        [TestCase(11L, false)]
+        public void HasFresh_uses_a_strict_greater_than_threshold(long minValidStamp, bool expected)
+        {
+            EndpointBondTable table = default;
+            table.Record(Endpoint(1), stamp: 10);
+
+            Assert.That(table.HasFresh(Endpoint(1), minValidStamp), Is.EqualTo(expected));
+        }
+
+        [Test]
+        public void HasFresh_only_matches_the_queried_endpoint()
+        {
+            EndpointBondTable table = default;
+            table.Record(Endpoint(1), stamp: 100);
+
+            Assert.That(table.HasFresh(Endpoint(1), minValidStamp: 0), Is.True);
+            Assert.That(table.HasFresh(Endpoint(2), minValidStamp: 0), Is.False);
+        }
+
+        [Test]
+        public void Contains_ignores_stamp_freshness()
+        {
+            EndpointBondTable table = default;
+            table.Record(Endpoint(1), stamp: 5);
+
+            // Contains never applies the freshness threshold; only HasFresh does.
+            Assert.That(table.Contains(Endpoint(1)), Is.True);
+            Assert.That(table.HasFresh(Endpoint(1), minValidStamp: 10), Is.False);
+        }
+
+        [Test]
+        public void Remove_requires_a_matching_stamp()
+        {
+            EndpointBondTable table = default;
+            table.Record(Endpoint(1), stamp: 42);
+
+            Assert.That(table.Remove(Endpoint(1), expectedStamp: 41), Is.False, "stale token must not remove a newer entry");
+            Assert.That(table.Contains(Endpoint(1)), Is.True);
+
+            Assert.That(table.Remove(Endpoint(1), expectedStamp: 42), Is.True);
+            Assert.That(table.Contains(Endpoint(1)), Is.False);
+            Assert.That(table.IsEmpty, Is.True);
+        }
+
+        [Test]
+        public void Remove_preserves_other_entries()
+        {
+            EndpointBondTable table = default;
+            table.Record(Endpoint(1), stamp: 1);
+            table.Record(Endpoint(2), stamp: 2);
+            table.Record(Endpoint(3), stamp: 3);
+
+            Assert.That(table.Remove(Endpoint(2), expectedStamp: 2), Is.True);
+
+            Assert.That(table.Count, Is.EqualTo(2));
+            Assert.That(table.Contains(Endpoint(1)), Is.True);
+            Assert.That(table.Contains(Endpoint(2)), Is.False);
+            Assert.That(table.Contains(Endpoint(3)), Is.True);
+        }
+
+        [Test]
+        public void PruneStale_drops_entries_at_or_below_threshold_and_keeps_fresher_ones()
+        {
+            EndpointBondTable table = default;
+            table.Record(Endpoint(1), stamp: 5);   // stale (== threshold)
+            table.Record(Endpoint(2), stamp: 3);   // stale (< threshold)
+            table.Record(Endpoint(3), stamp: 9);   // fresh
+
+            table.PruneStale(minValidStamp: 5);
+
+            Assert.That(table.Count, Is.EqualTo(1));
+            Assert.That(table.Contains(Endpoint(1)), Is.False);
+            Assert.That(table.Contains(Endpoint(2)), Is.False);
+            Assert.That(table.Contains(Endpoint(3)), Is.True);
+        }
+
+        [Test]
+        public void Record_stays_within_capacity()
+        {
+            EndpointBondTable table = default;
+
+            for (int i = 0; i < EndpointBondTable.Capacity; i++)
+            {
+                Assert.That(table.Record(Endpoint(i), stamp: i), Is.False, "no eviction while capacity remains");
+            }
+
+            Assert.That(table.Count, Is.EqualTo(EndpointBondTable.Capacity));
+
+            Assert.That(table.Record(Endpoint(EndpointBondTable.Capacity), stamp: EndpointBondTable.Capacity), Is.True, "table is full");
+            Assert.That(table.Count, Is.EqualTo(EndpointBondTable.Capacity), "count is bounded by capacity");
+        }
+
+        [Test]
+        public void Record_evicts_the_lowest_stamped_entry_when_full()
+        {
+            EndpointBondTable table = default;
+
+            // Fill to capacity; the endpoint at port 0 carries the lowest stamp but is not the last inserted.
+            table.Record(Endpoint(0), stamp: 1);
+            for (int i = 1; i < EndpointBondTable.Capacity; i++)
+            {
+                table.Record(Endpoint(i), stamp: 100 + i);
+            }
+
+            EndpointKey newest = Endpoint(EndpointBondTable.Capacity);
+            Assert.That(table.Record(newest, stamp: 500), Is.True);
+
+            Assert.That(table.Contains(Endpoint(0)), Is.False, "lowest-stamped entry is evicted");
+            Assert.That(table.Contains(newest), Is.True);
+            for (int i = 1; i < EndpointBondTable.Capacity; i++)
+            {
+                Assert.That(table.Contains(Endpoint(i)), Is.True, $"higher-stamped entry {i} is retained");
+            }
+        }
+
+        [Test]
+        public void Record_refreshes_existing_endpoint_without_eviction_when_full()
+        {
+            EndpointBondTable table = default;
+            for (int i = 0; i < EndpointBondTable.Capacity; i++)
+            {
+                table.Record(Endpoint(i), stamp: i);
+            }
+
+            Assert.That(table.Record(Endpoint(0), stamp: 500), Is.False);
+
+            Assert.That(table.Count, Is.EqualTo(EndpointBondTable.Capacity));
+            Assert.That(table.HasFresh(Endpoint(0), minValidStamp: 499), Is.True);
+            for (int i = 1; i < EndpointBondTable.Capacity; i++)
+            {
+                Assert.That(table.Contains(Endpoint(i)), Is.True, $"entry {i} should not be evicted");
+            }
+        }
+    }
+}
```

### src/Nethermind/Nethermind.Network.Discovery.Test/Discv4/Kademlia/KademliaAdapterTests.cs
```diff
@@ -1,4 +1,4 @@
-// SPDX-FileCopyrightText: 2025 Demerzel Solutions Limited
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using System;
@@ -70,7 +70,7 @@ public enum NoResponseRequest
         private IMessageSerializationService _receiverSerializationManager;
         private Node _receiver;
 
-        private void ConfigureBondCallback() =>
+        private void ConfigureBondCallback(IPEndPoint? pongFarAddress = null, ulong? pongEnrSequence = null) =>
             _msgSender
                 .SendMsg(Arg.Any<PingMsg>())
                 .Returns(ci =>
@@ -81,8 +81,9 @@ private void ConfigureBondCallback() =>
                     PongMsg pong = new(
                         msg.FarPublicKey!,
                         _timestamper.UnixTime.SecondsLong + 1,
-                        sent.Mdc!.Value);
-                    pong.FarAddress = sent.FarAddress;
+                        sent.Mdc!.Value,
+                        pongEnrSequence);
+                    pong.FarAddress = pongFarAddress ?? sent.FarAddress;
                     return _adapter.OnIncomingMsg(pong);
                 });
 
@@ -253,6 +254,32 @@ await _msgSender.Received(1).SendMsg(Arg.Is<PingMsg>(m =>
                 m.FarAddress!.Equals(_receiver.Address)));
         }
 
+        [Test]
+        [CancelAfter(10000)]
+        public async Task Ping_should_not_bond_requested_endpoint_when_pong_source_differs(CancellationToken token)
+        {
+            IPEndPoint pongFarAddress = new(IPAddress.Parse("192.168.1.4"), _receiver.Address.Port);
+            ConfigureBondCallback(pongFarAddress, pongEnrSequence: 42);
+
+            bool result = await _adapter.Ping(_receiver, token);
+            Assert.That(result, Is.False);
+            await _msgSender.DidNotReceive().SendMsg(Arg.Any<EnrRequestMsg>());
+            _msgSender.ClearReceivedCalls();
+
+            FindNodeMsg findNodeMsg = new(_receiver.Address, _timestamper.UnixTime.SecondsLong + 20, _testPublicKey.Bytes);
+            findNodeMsg = AddReceiverFarAddress(findNodeMsg);
+
+            Node[] expectedNodes = [new(TestItem.PublicKeyD, "192.168.1.3", 30303)];
+            _kademliaMessageReceiver.GetKNeighbour(
+                Arg.Any<PublicKey>(),
+                Arg.Any<Node>())
+                .Returns(expectedNodes);
+
+            await _adapter.OnIncomingMsg(findNodeMsg);
+
+            await _msgSender.DidNotReceive().SendMsg(Arg.Any<NeighborsMsg>());
+        }
+
         [Test]
         [CancelAfter(10000)]
         public async Task FindNeighbours_should_return_nodes(CancellationToken token)
@@ -364,9 +391,7 @@ public async Task Ping_should_refresh_remote_enr_from_advertised_sequence(
             if (shouldCacheEnr)
             {
                 _kademliaMessageReceiver.Received(1).AddOrRefresh(Arg.Is<Node>(n =>
-                    n.Id.Equals(_receiver.Id) &&
-                    n.Enr != null &&
-                    n.Enr.ToString() == remoteRecord.ToString()));
+                    HasNodeRecord(n, _receiver, remoteRecord)));
             }
             else
             {
@@ -500,6 +525,70 @@ await _msgSender.Received(1).SendMsg(Arg.Is<PongMsg>(m =>
                 m.PingMdc == expectedPingMdc));
         }
 
+        [Test]
+        [CancelAfter(10000)]
+        public async Task OnIncomingMsg_ping_with_trailing_enr_sequence_should_not_request_remote_enr(CancellationToken token)
+        {
+            ConfigureBondCallback();
+
+            PingMsg pingMsg = new(_receiver.Address, _timestamper.UnixTime.SecondsLong + 20, _kademliaConfig.CurrentNodeId.Address)
+            {
+                EnrSequence = 42
+            };
+            pingMsg.FarAddress = _receiver.Address;
+            pingMsg = AddReceiverFarAddress(pingMsg);
+
+            await _adapter.OnIncomingMsg(pingMsg);
+
+            await _msgSender.Received(1).SendMsg(Arg.Is<PongMsg>(m => m.FarAddress!.Equals(_receiver.Address)));
+            await _msgSender.Received(1).SendMsg(Arg.Is<PingMsg>(m => m.FarAddress!.Equals(_receiver.Address)));
+            await _msgSender.DidNotReceive().SendMsg(Arg.Any<EnrRequestMsg>());
+        }
+
+        [Test]
+        [CancelAfter(10000)]
+        public async Task OnIncomingMsg_ping_from_bonded_peer_should_refresh_remote_enr(CancellationToken token)
+        {
+            await BondReceiver(token);
+            NodeRecord remoteRecord = ConfigureRemoteEnrRefresh(42, 42);
+
+            PingMsg pingMsg = new(_receiver.Address, _timestamper.UnixTime.SecondsLong + 20, _kademliaConfig.CurrentNodeId.Address)
+            {
+                EnrSequence = 42
+            };
+            pingMsg.FarAddress = _receiver.Address;
+            pingMsg = AddReceiverFarAddress(pingMsg);
+
+            await _adapter.OnIncomingMsg(pingMsg);
+
+            await _msgSender.Received(1).SendMsg(Arg.Is<EnrRequestMsg>(m => m.FarAddress!.Equals(_receiver.Address)));
+            _kademliaMessageReceiver.Received(1).AddOrRefresh(Arg.Is<Node>(n =>
+                HasNodeRecord(n, _receiver, remoteRecord)));
+        }
+
+        [Test]
+        [CancelAfter(10000)]
+        public async Task OnIncomingMsg_ping_from_bonded_node_at_unbonded_endpoint_should_send_bonding_ping(CancellationToken token)
+        {
+            ConfigureBondCallback();
+            await BondReceiver(token);
+            _msgSender.ClearReceivedCalls();
+
+            IPEndPoint differentEndpoint = new(IPAddress.Parse("192.168.1.3"), _receiver.Address.Port);
+            PingMsg pingMsg = new(differentEndpoint, _timestamper.UnixTime.SecondsLong + 20, _kademliaConfig.CurrentNodeId.Address)
+            {
+                EnrSequence = 42
+            };
+            pingMsg.FarAddress = differentEndpoint;
+            pingMsg = AddReceiverFarAddress(pingMsg);
+
+            await _adapter.OnIncomingMsg(pingMsg);
+
+            await _msgSender.Received(1).SendMsg(Arg.Is<PongMsg>(m => m.FarAddress!.Equals(differentEndpoint)));
+            await _msgSender.Received(1).SendMsg(Arg.Is<PingMsg>(m => m.FarAddress!.Equals(differentEndpoint)));
+            await _msgSender.DidNotReceive().SendMsg(Arg.Any<EnrRequestMsg>());
+        }
+
         [Test]
         [CancelAfter(10000)]
         public async Task OnIncomingMsg_find_node_should_respond_with_neighbors(CancellationToken token)
@@ -579,6 +668,42 @@ await _msgSender.Received(1).SendMsg(Arg.Is<EnrResponseMsg>(m =>
                 m.NodeRecord.Equals(_selfNodeRecord)));
         }
 
+        [Test]
+        [CancelAfter(10000)]
+        public async Task OnIncomingMsg_enr_request_after_inbound_ping_without_endpoint_bond_should_not_respond(CancellationToken token)
+        {
+            _adapter.GetSession(_receiver).OnPingReceived(_receiver.Address);
+
+            EnrRequestMsg enrRequestMsg = new(_receiver.Address, _timestamper.UnixTime.SecondsLong + 20);
+            enrRequestMsg = AddReceiverFarAddress(enrRequestMsg);
+
+            await _adapter.OnIncomingMsg(enrRequestMsg);
+
+            await _msgSender.DidNotReceive().SendMsg(Arg.Any<EnrResponseMsg>());
+        }
+
+        [Test]
+        [CancelAfter(10000)]
+        public async Task OnIncomingMsg_enr_request_after_inbound_ping_from_different_endpoint_should_not_respond(CancellationToken token)
+        {
+            ConfigureBondCallback();
+
+            PingMsg pingMsg = new(_receiver.Address, _timestamper.UnixTime.SecondsLong + 20, _kademliaConfig.CurrentNodeId.Address);
+            pingMsg.FarAddress = _receiver.Address;
+            pingMsg = AddReceiverFarAddress(pingMsg);
+
+            await _adapter.OnIncomingMsg(pingMsg);
+            _msgSender.ClearReceivedCalls();
+
+            IPEndPoint differentEndpoint = new(IPAddress.Parse("192.168.1.3"), _receiver.Address.Port);
+            EnrRequestMsg enrRequestMsg = new(differentEndpoint, _timestamper.UnixTime.SecondsLong + 20);
+            enrRequestMsg = AddReceiverFarAddress(enrRequestMsg);
+
+            await _adapter.OnIncomingMsg(enrRequestMsg);
+
+            await _msgSender.DidNotReceive().SendMsg(Arg.Any<EnrResponseMsg>());
+        }
+
         [Test]
         [CancelAfter(10000)]
         public async Task OnIncomingMsg_enr_request_from_unbonded_peer_should_not_update_node_health(CancellationToken token)
@@ -591,5 +716,10 @@ public async Task OnIncomingMsg_enr_request_from_unbonded_peer_should_not_update
             _nodeHealthTracker.DidNotReceive().OnIncomingMessageFrom(Arg.Is<Node>(n => n.Id == _receiver.Id));
             await _msgSender.DidNotReceive().SendMsg(Arg.Any<EnrResponseMsg>());
         }
+
+        private static bool HasNodeRecord(Node node, Node expectedNode, NodeRecord expectedRecord) =>
+            node.Id.Equals(expectedNode.Id) &&
+            node.Enr is not null &&
+            node.Enr.ToString() == expectedRecord.ToString();
     }
 }
```

### src/Nethermind/Nethermind.Network.Discovery.Test/Discv4/NodeSessionTests.cs
```diff
@@ -1,8 +1,10 @@
-// SPDX-FileCopyrightText: 2025 Demerzel Solutions Limited
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using System;
 using System.Net;
+using System.Threading;
+using System.Threading.Tasks;
 using Nethermind.Core;
 using Nethermind.Network.Discovery.Discv4;
 using Nethermind.Stats;
@@ -34,7 +36,7 @@ public void Setup()
         [
             new TestCaseData(
                 (Func<NodeSession, bool>)(s => s.HasReceivedPing),
-                (Action<NodeSession>)(s => s.OnPingReceived()),
+                (Action<NodeSession>)(s => s.OnPingReceived(TestEndpoint)),
                 NodeSession.BondTimeout).SetName(nameof(NodeSession.HasReceivedPing)),
             new TestCaseData(
                 (Func<NodeSession, bool>)(s => s.HasReceivedPong),
@@ -46,6 +48,18 @@ public void Setup()
                 NodeSession.PingRetryTimeout).SetName(nameof(NodeSession.HasTriedPingRecently)),
         ];
 
+        private static readonly TestCaseData[] RememberedEndpointCapacityCases =
+        [
+            new TestCaseData(
+                (Action<NodeSession, IPEndPoint>)((session, endpoint) => session.OnPingReceived(endpoint)),
+                (Func<NodeSession, IPEndPoint, bool>)((session, endpoint) => session.HasReceivedPingFrom(endpoint)))
+                .SetName("HasReceivedPingFrom_caps_remembered_endpoints"),
+            new TestCaseData(
+                (Action<NodeSession, IPEndPoint>)((session, endpoint) => session.OnPongReceived(endpoint)),
+                (Func<NodeSession, IPEndPoint, bool>)((session, endpoint) => session.HasEndpointBond(endpoint)))
+                .SetName("HasEndpointBond_caps_remembered_endpoints"),
+        ];
+
         [TestCaseSource(nameof(FlagTimeoutCases))]
         public void Flag_is_set_on_event_and_cleared_after_timeout(
             Func<NodeSession, bool> getter,
@@ -59,6 +73,134 @@ public void Flag_is_set_on_event_and_cleared_after_timeout(
             Assert.That(getter(_nodeSession), Is.False);
         }
 
+        [Test]
+        public void HasReceivedPingFrom_requires_matching_endpoint()
+        {
+            IPEndPoint differentEndpoint = new(IPAddress.Parse("192.168.1.1"), TestEndpoint.Port);
+
+            _nodeSession.OnPingReceived(TestEndpoint);
+
+            Assert.That(_nodeSession.HasReceivedPingFrom(TestEndpoint), Is.True);
+            Assert.That(_nodeSession.HasReceivedPingFrom(differentEndpoint), Is.False);
+        }
+
+        [Test]
+        public void HasReceivedPingFrom_keeps_received_pings_for_each_endpoint()
+        {
+            IPEndPoint otherEndpoint = new(IPAddress.Parse("192.168.1.1"), TestEndpoint.Port);
+
+            _nodeSession.OnPingReceived(TestEndpoint);
+            _nodeSession.OnPingReceived(otherEndpoint);
+
+            Assert.That(_nodeSession.HasReceivedPingFrom(TestEndpoint), Is.True);
+            Assert.That(_nodeSession.HasReceivedPingFrom(otherEndpoint), Is.True);
+        }
+
+        [Test]
+        public void HasEndpointBond_keeps_bonds_for_each_endpoint()
+        {
+            IPEndPoint otherEndpoint = new(IPAddress.Parse("192.168.1.1"), TestEndpoint.Port);
+
+            _nodeSession.OnPongReceived(TestEndpoint);
+            _nodeSession.OnPongReceived(otherEndpoint);
+
+            Assert.That(_nodeSession.HasEndpointBond(TestEndpoint), Is.True);
+            Assert.That(_nodeSession.HasEndpointBond(otherEndpoint), Is.True);
+        }
+
+        [TestCaseSource(nameof(RememberedEndpointCapacityCases))]
+        public void Remembered_endpoint_state_is_capped(
+            Action<NodeSession, IPEndPoint> recordEndpoint,
+            Func<NodeSession, IPEndPoint, bool> hasEndpoint)
+        {
+            IPEndPoint oldestEndpoint = new(IPAddress.Parse("192.168.1.1"), TestEndpoint.Port);
+            IPEndPoint newestEndpoint = null!;
+
+            recordEndpoint(_nodeSession, oldestEndpoint);
+            for (int i = 0; i < EndpointBondTable.Capacity; i++)
+            {
+                _timestamper.Add(TimeSpan.FromTicks(1));
+                newestEndpoint = new(IPAddress.Parse("192.168.1.1"), TestEndpoint.Port + i + 1);
+                recordEndpoint(_nodeSession, newestEndpoint);
+            }
+
+            Assert.That(hasEndpoint(_nodeSession, oldestEndpoint), Is.False);
+            Assert.That(hasEndpoint(_nodeSession, newestEndpoint), Is.True);
+        }
+
+        [Test]
+        public async Task WaitForEndpointBond_completes_when_matching_pong_is_received()
+        {
+            _nodeSession.OnPingSent(TestEndpoint);
+
+            Task<bool> waitTask = _nodeSession
+                .WaitForEndpointBond(TestEndpoint, TimeSpan.FromSeconds(1), CancellationToken.None)
+                .AsTask();
+
+            Assert.That(waitTask.IsCompleted, Is.False);
+
+            _nodeSession.OnPongReceived(TestEndpoint);
+
+            Assert.That(await waitTask, Is.True);
+        }
+
+        [Test]
+        public async Task WaitForEndpointBond_keeps_pending_bonding_pings_for_each_endpoint()
+        {
+            IPEndPoint otherEndpoint = new(IPAddress.Parse("192.168.1.1"), TestEndpoint.Port);
+
+            _nodeSession.OnPingSent(TestEndpoint);
+            _nodeSession.OnPingSent(otherEndpoint);
+
+            Task<bool> waitTask = _nodeSession
+                .WaitForEndpointBond(TestEndpoint, TimeSpan.FromSeconds(1), CancellationToken.None)
+                .AsTask();
+
+            Assert.That(waitTask.IsCompleted, Is.False);
+
+            _nodeSession.OnPongReceived(TestEndpoint);
+
+            Assert.That(await waitTask, Is.True);
+        }
+
+        [Test]
+        public void HasPendingBondingPing_caps_pending_endpoints()
+        {
+            IPEndPoint oldestEndpoint = new(IPAddress.Parse("192.168.1.1"), TestEndpoint.Port);
+            IPEndPoint newestEndpoint = null!;
+
+            _nodeSession.OnPingSent(oldestEndpoint);
+            for (int i = 0; i < EndpointBondTable.Capacity; i++)
+            {
+                newestEndpoint = new(IPAddress.Parse("192.168.1.1"), TestEndpoint.Port + i + 1);
+                _nodeSession.OnPingSent(newestEndpoint);
+            }
+
+            Assert.That(_nodeSession.HasPendingBondingPing(oldestEndpoint), Is.False);
+            Assert.That(_nodeSession.HasPendingBondingPing(newestEndpoint), Is.True);
+        }
+
+        [Test]
+        public async Task WaitForEndpointBond_completes_when_pending_ping_is_evicted()
+        {
+            IPEndPoint oldestEndpoint = new(IPAddress.Parse("192.168.1.1"), TestEndpoint.Port);
+
+            _nodeSession.OnPingSent(oldestEndpoint);
+            Task<bool> waitTask = _nodeSession
+                .WaitForEndpointBond(oldestEndpoint, TimeSpan.FromMinutes(1), CancellationToken.None)
+                .AsTask();
+
+            Assert.That(waitTask.IsCompleted, Is.False);
+
+            for (int i = 0; i < EndpointBondTable.Capacity; i++)
+            {
+                IPEndPoint endpoint = new(IPAddress.Parse("192.168.1.1"), TestEndpoint.Port + i + 1);
+                _nodeSession.OnPingSent(endpoint);
+            }
+
+            Assert.That(await waitTask, Is.False);
+        }
+
         [Test]
         public void Test_NotTooManyFailures()
         {
```

### src/Nethermind/Nethermind.Network.Discovery.Test/Discv5/KademliaAdapterTests.cs
```diff
@@ -127,6 +127,24 @@ public void TryGetKnownSignedRecord_ShouldScanOnlyMatchingBucket()
         _kademlia.DidNotReceive().IterateNodes();
     }
 
+    [Test]
+    public void HasDiscoveryEndpoint_ShouldRequireExactEndpoint()
+    {
+        IPEndPoint endpoint = IPEndPoint.Parse("172.19.0.2:30304");
+        NodeRecord record = TestEnrBuilder.BuildSigned(
+            TestItem.PrivateKeyB,
+            endpoint.Address,
+            tcpPort: null,
+            udpPort: endpoint.Port);
+
+        using (Assert.EnterMultipleScope())
+        {
+            Assert.That(KademliaAdapter.HasDiscoveryEndpoint(record, endpoint), Is.True);
+            Assert.That(KademliaAdapter.HasDiscoveryEndpoint(record, IPEndPoint.Parse("172.17.0.1:30304")), Is.False);
+            Assert.That(KademliaAdapter.HasDiscoveryEndpoint(record, IPEndPoint.Parse("172.19.0.2:30305")), Is.False);
+        }
+    }
+
     [TestCaseSource(nameof(AcceptableNodeRecordCases))]
     public void IsAcceptableNodeRecord_ShouldValidateRecord(AcceptableNodeRecordCase testCase)
     {
```

### src/Nethermind/Nethermind.Network.Discovery.Test/Discv5/WireTests.cs
```diff
@@ -3,6 +3,7 @@
 
 using System;
 using System.Collections.Concurrent;
+using System.Collections.Generic;
 using System.Diagnostics.CodeAnalysis;
 using System.Net;
 using System.Threading;
@@ -57,8 +58,8 @@ public async Task Ping_Completes_After_WhoAreYou_Handshake()
         await cancellationSource.CancelAsync();
         await Task.WhenAll(runA, runB);
 
-        peerA.Kademlia.Received().AddOrRefresh(Arg.Is<Node>(node => node.Id.Equals(TestItem.PrivateKeyB.PublicKey) && node.Enr != null));
-        peerB.Kademlia.Received().AddOrRefresh(Arg.Is<Node>(node => node.Id.Equals(TestItem.PrivateKeyA.PublicKey) && node.Enr != null));
+        peerA.Kademlia.Received().AddOrRefresh(Arg.Is<Node>(node => node.Id.Equals(TestItem.PrivateKeyB.PublicKey) && HasEnr(node)));
+        peerB.Kademlia.Received().AddOrRefresh(Arg.Is<Node>(node => node.Id.Equals(TestItem.PrivateKeyA.PublicKey) && HasEnr(node)));
     }
 
     [Test]
@@ -160,7 +161,7 @@ public async Task Ping_Completes_With_HandshakeRecord_WithoutEndpoint()
         await cancellationSource.CancelAsync();
         await Task.WhenAll(runA, runB);
 
-        peerB.Kademlia.Received().AddOrRefresh(Arg.Is<Node>(node => node.Id.Equals(TestItem.PrivateKeyA.PublicKey) && node.Enr == null));
+        peerB.Kademlia.Received().AddOrRefresh(Arg.Is<Node>(node => node.Id.Equals(TestItem.PrivateKeyA.PublicKey) && !HasEnr(node)));
     }
 
     [Test]
@@ -238,9 +239,112 @@ public async Task FindNeighbours_Returns_Records_At_Requested_Distance()
         peerA.Kademlia.Received().AddOrRefresh(Arg.Is<Node>(node => node.Id.Equals(TestItem.PrivateKeyC.PublicKey)));
     }
 
-    private static TestPeer CreatePeer(PrivateKey privateKey, IPEndPoint endpoint, bool includeEndpointInRecord = true, ulong enrSequence = 1)
+    [Test]
+    public async Task FindNeighbours_ShouldPreferValidatedRecords_WhenBucketHasMoreThanResponseLimit()
+    {
+        IPEndPoint endpointA = IPEndPoint.Parse("127.0.0.1:10000");
+        IPEndPoint endpointB = IPEndPoint.Parse("127.0.0.1:10001");
+        await using TestPeer peerA = CreatePeer(TestItem.PrivateKeyA, endpointA);
+        await using TestPeer peerB = CreatePeer(TestItem.PrivateKeyB, endpointB);
+        Node nodeB = new(TestItem.PrivateKeyB.PublicKey, endpointB)
+        {
+            Enr = peerB.NodeRecordProvider.Current
+        };
+
+        Node[] bucketNodes = new Node[17];
+        for (int i = 0; i < 16; i++)
+        {
+            bucketNodes[i] = CreateSignedNode(TestItem.PrivateKeys[i], IPEndPoint.Parse($"127.0.0.1:{11000 + i}"));
+        }
+
+        Node validatedNode = CreateSignedNode(TestItem.PrivateKeyD, IPEndPoint.Parse("127.0.0.1:12000"));
+        validatedNode.ValidatedProtocol = true;
+        bucketNodes[^1] = validatedNode;
+
+        using Distances requestedDistances = peerA.Adapter.GetLookupDistances(nodeB, validatedNode.Id);
+        for (int i = 0; i < requestedDistances.Count; i++)
+        {
+            peerB.Kademlia.GetAllAtDistance(requestedDistances[i]).Returns([]);
+        }
+
+        peerB.Kademlia.GetAllAtDistance(requestedDistances[0]).Returns(bucketNodes);
+
+        using CancellationTokenSource cancellationSource = new(10_000);
+        Task runA = peerA.Adapter.RunAsync(cancellationSource.Token);
+        Task runB = peerB.Adapter.RunAsync(cancellationSource.Token);
+
+        Task<Node[]?> findTask = peerA.Adapter.FindNeighbours(nodeB, validatedNode.Id, cancellationSource.Token);
+        await PumpUntilComplete(findTask, peerA, peerB, cancellationSource.Token);
+        Node[]? nodes = await findTask;
+
+        await cancellationSource.CancelAsync();
+        await Task.WhenAll(runA, runB);
+
+        Assert.That(nodes, Is.Not.Null);
+        Assert.That(nodes, Has.Length.LessThanOrEqualTo(16));
+        Assert.That(nodes, Has.One.Matches<Node>(node => node.Id.Equals(validatedNode.Id)));
+    }
+
+    [Test]
+    public async Task EndpointCheck_ShouldAdmitValidatedNode_WhenBucketPromotesUnvalidatedReplacement()
+    {
+        IPEndPoint endpointA = IPEndPoint.Parse("127.0.0.1:10000");
+        IPEndPoint endpointB = IPEndPoint.Parse("127.0.0.1:10001");
+        IPEndPoint endpointC = IPEndPoint.Parse("127.0.0.1:10002");
+        FindKeysAtSameDistance(
+            TestItem.PrivateKeyA.PublicKey.Hash,
+            out PrivateKey staleKey,
+            out PrivateKey replacementKey,
+            out PrivateKey liveKey);
+
+        BoundedDistanceKademlia table = new(TestItem.PrivateKeyA.PublicKey.Hash, capacityPerDistance: 1);
+        Node staleNode = CreateSignedNode(staleKey, IPEndPoint.Parse("127.0.0.1:11000"));
+        Node replacementNode = CreateSignedNode(replacementKey, IPEndPoint.Parse("127.0.0.1:11001"));
+        table.AddOrRefresh(staleNode);
+        table.AddReplacement(replacementNode);
+
+        await using TestPeer peerA = CreatePeer(TestItem.PrivateKeyA, endpointA, kademlia: table, bucketSize: 1);
+        await using TestPeer peerB = CreatePeer(liveKey, endpointB);
+        await using TestPeer peerC = CreatePeer(TestItem.PrivateKeyC, endpointC);
+        Node nodeA = new(TestItem.PrivateKeyA.PublicKey, endpointA)
+        {
+            Enr = peerA.NodeRecordProvider.Current
+        };
+
+        using CancellationTokenSource cancellationSource = new(10_000);
+        Task runA = peerA.Adapter.RunAsync(cancellationSource.Token);
+        Task runB = peerB.Adapter.RunAsync(cancellationSource.Token);
+        Task runC = peerC.Adapter.RunAsync(cancellationSource.Token);
+
+        Task pingTask = peerB.Adapter.Ping(nodeA, cancellationSource.Token);
+        await PumpUntilComplete(pingTask, peerB, peerA, cancellationSource.Token);
+        await pingTask;
+        await PumpUntil(
+            () => table.Contains(liveKey.PublicKey) && !table.Contains(replacementKey.PublicKey),
+            peerA,
+            peerB,
+            cancellationSource.Token);
+
+        Task<Node[]?> findTask = peerC.Adapter.FindNeighbours(nodeA, liveKey.PublicKey, cancellationSource.Token);
+        await PumpUntilComplete(findTask, peerC, peerA, cancellationSource.Token);
+        Node[]? nodes = await findTask;
+
+        await cancellationSource.CancelAsync();
+        await Task.WhenAll(runA, runB, runC);
+
+        Assert.That(nodes, Is.Not.Null);
+        Assert.That(nodes, Has.One.Matches<Node>(node => node.Id.Equals(liveKey.PublicKey)));
+    }
+
+    private static TestPeer CreatePeer(
+        PrivateKey privateKey,
+        IPEndPoint endpoint,
+        bool includeEndpointInRecord = true,
+        ulong enrSequence = 1,
+        IKademlia<PublicKey, Node>? kademlia = null,
+        int bucketSize = 16)
     {
-        IKademlia<PublicKey, Node> kademlia = Substitute.For<IKademlia<PublicKey, Node>>();
+        IKademlia<PublicKey, Node> table = kademlia ?? Substitute.For<IKademlia<PublicKey, Node>>();
         NettyDiscoveryV5Handler handler = new(new TestLogManager());
         EmbeddedChannel channel = new();
         OutboundDatagramCapture outbound = new();
@@ -254,18 +358,18 @@ private static TestPeer CreatePeer(PrivateKey privateKey, IPEndPoint endpoint, b
             new EthereumEcdsa(0));
         Node currentNode = new(privateKey.PublicKey, endpoint, true);
         KademliaAdapter adapter = new(
-            new Lazy<IKademlia<PublicKey, Node>>(kademlia),
+            new Lazy<IKademlia<PublicKey, Node>>(table),
             handler,
             packetCodec,
             nodeRecordProvider,
             new DiscoveryConfig(),
-            new KademliaConfig<Node> { CurrentNodeId = currentNode },
+            new KademliaConfig<Node> { CurrentNodeId = currentNode, KSize = bucketSize },
             new CryptoRandom(),
             Hash256KademliaDistance.Instance,
             ExecutionLayerDiscv5RecordFilter.Instance,
             LimboLogs.Instance);
 
-        return new TestPeer(adapter, handler, channel, outbound, packetCodec, kademlia, nodeRecordProvider, endpoint);
+        return new TestPeer(adapter, handler, channel, outbound, packetCodec, table, nodeRecordProvider, endpoint);
     }
 
     private static async Task PumpUntilComplete(Task task, TestPeer peerA, TestPeer peerB, CancellationToken token)
@@ -311,6 +415,8 @@ private static bool HasEnrSequence(Node node, ulong sequence)
         }
     }
 
+    private static bool HasEnr(Node node) => node.Enr is not null;
+
     private static bool HasReceivedNodeWithEnrSequence(IKademlia<PublicKey, Node> kademlia, PublicKey publicKey, ulong sequence)
     {
         foreach (NSubstitute.Core.ICall call in kademlia.ReceivedCalls())
@@ -327,6 +433,48 @@ private static bool HasReceivedNodeWithEnrSequence(IKademlia<PublicKey, Node> ka
         return false;
     }
 
+    private static void FindKeysAtSameDistance(
+        Hash256 currentNodeHash,
+        out PrivateKey firstKey,
+        out PrivateKey secondKey,
+        out PrivateKey thirdKey)
+    {
+        Dictionary<int, List<PrivateKey>> keysByDistance = [];
+        for (int i = 0; i < TestItem.PrivateKeys.Length; i++)
+        {
+            PrivateKey candidate = TestItem.PrivateKeys[i];
+            if (candidate.PublicKey.Equals(TestItem.PrivateKeyA.PublicKey) ||
+                candidate.PublicKey.Equals(TestItem.PrivateKeyC.PublicKey))
+            {
+                continue;
+            }
+
+            int distance = Hash256KademliaDistance.Instance.CalculateLogDistance(currentNodeHash, candidate.PublicKey.Hash);
+            if (!keysByDistance.TryGetValue(distance, out List<PrivateKey>? keys))
+            {
+                keys = [];
+                keysByDistance[distance] = keys;
+            }
+
+            keys.Add(candidate);
+            if (keys.Count == 3)
+            {
+                firstKey = keys[0];
+                secondKey = keys[1];
+                thirdKey = keys[2];
+                return;
+            }
+        }
+
+        throw new InvalidOperationException("Could not find three test keys at the same discv5 distance.");
+    }
+
+    private static Node CreateSignedNode(PrivateKey privateKey, IPEndPoint endpoint)
+        => new(privateKey.PublicKey, endpoint)
+        {
+            Enr = TestEnrBuilder.BuildSigned(privateKey, endpoint.Address, tcpPort: endpoint.Port, udpPort: endpoint.Port)
+        };
+
     private static void Pump(TestPeer from, TestPeer to)
     {
         while (from.Outbound.TryDequeue(out DatagramPacket? packet))
@@ -344,6 +492,181 @@ private static void Pump(TestPeer from, TestPeer to)
         }
     }
 
+    private sealed class BoundedDistanceKademlia(Hash256 currentNodeHash, int capacityPerDistance) : IKademlia<PublicKey, Node>
+    {
+        private readonly object _lock = new();
+        private readonly Dictionary<int, List<Node>> _nodesByDistance = [];
+        private readonly Dictionary<int, List<Node>> _replacementsByDistance = [];
+
+        public event EventHandler<Node>? OnNodeAdded;
+        public event EventHandler<Node>? OnNodeRemoved;
+
+        public void AddOrRefresh(Node node)
+        {
+            int distance = Hash256KademliaDistance.Instance.CalculateLogDistance(currentNodeHash, node.Id.Hash);
+            bool added = false;
+            lock (_lock)
+            {
+                List<Node> nodes = GetNodes(distance);
+                for (int i = 0; i < nodes.Count; i++)
+                {
+                    if (nodes[i].Id.Equals(node.Id))
+                    {
+                        nodes[i] = node;
+                        return;
+                    }
+                }
+
+                if (nodes.Count >= capacityPerDistance)
+                {
+                    return;
+                }
+
+                nodes.Add(node);
+                added = true;
+            }
+
+            if (added)
+            {
+                OnNodeAdded?.Invoke(this, node);
+            }
+        }
+
+        public void AddReplacement(Node node)
+        {
+            int distance = Hash256KademliaDistance.Instance.CalculateLogDistance(currentNodeHash, node.Id.Hash);
+            lock (_lock)
+            {
+                GetReplacements(distance).Add(node);
+            }
+        }
+
+        public void Remove(Node node)
+        {
+            int distance = Hash256KademliaDistance.Instance.CalculateLogDistance(currentNodeHash, node.Id.Hash);
+            Node? removed = null;
+            lock (_lock)
+            {
+                if (!_nodesByDistance.TryGetValue(distance, out List<Node>? nodes))
+                {
+                    return;
+                }
+
+                for (int i = 0; i < nodes.Count; i++)
+                {
+                    if (!nodes[i].Id.Equals(node.Id))
+                    {
+                        continue;
+                    }
+
+                    removed = nodes[i];
+                    nodes.RemoveAt(i);
+                    PromoteReplacement(distance, nodes);
+                    break;
+                }
+            }
+
+            if (removed is not null)
+            {
+                OnNodeRemoved?.Invoke(this, removed);
+            }
+        }
+
+        public bool Contains(PublicKey publicKey)
+        {
+            int distance = Hash256KademliaDistance.Instance.CalculateLogDistance(currentNodeHash, publicKey.Hash);
+            lock (_lock)
+            {
+                if (!_nodesByDistance.TryGetValue(distance, out List<Node>? nodes))
+                {
+                    return false;
+                }
+
+                for (int i = 0; i < nodes.Count; i++)
+                {
+                    if (nodes[i].Id.Equals(publicKey))
+                    {
+                        return true;
+                    }
+                }
+
+                return false;
+            }
+        }
+
+        public Task Run(CancellationToken token) => throw new NotSupportedException();
+
+        public Task Bootstrap(CancellationToken token) => throw new NotSupportedException();
+
+        public Task<Node[]> LookupNodesClosest(PublicKey key, CancellationToken token, int? k = null) => throw new NotSupportedException();
+
+        public IAsyncEnumerable<Node> LookupNodes(PublicKey key, CancellationToken token, int? maxResults = null) => throw new NotSupportedException();
+
+        public Node[] GetKNeighbour(PublicKey target, Node? excluding = null, bool excludeSelf = false) => throw new NotSupportedException();
+
+        public Node[] GetAllAtDistance(int distance)
+        {
+            lock (_lock)
+            {
+                return _nodesByDistance.TryGetValue(distance, out List<Node>? nodes) ? nodes.ToArray() : [];
+            }
+        }
+
+        public IEnumerable<Node> IterateNodes()
+        {
+            Node[] snapshot;
+            lock (_lock)
+            {
+                List<Node> nodes = [];
+                foreach (List<Node> bucketNodes in _nodesByDistance.Values)
+                {
+                    nodes.AddRange(bucketNodes);
+                }
+
+                snapshot = nodes.ToArray();
+            }
+
+            for (int i = 0; i < snapshot.Length; i++)
+            {
+                yield return snapshot[i];
+            }
+        }
+
+        private List<Node> GetNodes(int distance)
+        {
+            if (!_nodesByDistance.TryGetValue(distance, out List<Node>? nodes))
+            {
+                nodes = [];
+                _nodesByDistance[distance] = nodes;
+            }
+
+            return nodes;
+        }
+
+        private List<Node> GetReplacements(int distance)
+        {
+            if (!_replacementsByDistance.TryGetValue(distance, out List<Node>? replacements))
+            {
+                replacements = [];
+                _replacementsByDistance[distance] = replacements;
+            }
+
+            return replacements;
+        }
+
+        private void PromoteReplacement(int distance, List<Node> nodes)
+        {
+            if (!_replacementsByDistance.TryGetValue(distance, out List<Node>? replacements) || replacements.Count == 0)
+            {
+                return;
+            }
+
+            Node replacement = replacements[0];
+            replacements.RemoveAt(0);
+            nodes.Add(replacement);
+        }
+    }
+
     private sealed record TestPeer(
         KademliaAdapter Adapter,
         NettyDiscoveryV5Handler Handler,
```

### src/Nethermind/Nethermind.Network.Discovery/DiscoveryConfig.cs
```diff
@@ -43,7 +43,7 @@ public class DiscoveryConfig : IDiscoveryConfig
 
     public float DropFullBucketNodeProbability { get; set; } = 0.05f;
 
-    public int MaxOutgoingMessagePerSecond { get; set; } = 100;
+    public int MaxOutgoingMessagePerSecond { get; set; } = 500;
 
     public NetworkNode[] Bootnodes { get; set; } = [];
 
```

### src/Nethermind/Nethermind.Network.Discovery/Discv4/EndpointBondTable.cs
```diff
@@ -0,0 +1,140 @@
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
+// SPDX-License-Identifier: LGPL-3.0-only
+
+using System.Net;
+
+namespace Nethermind.Network.Discovery.Discv4;
+
+internal readonly record struct EndpointKey(IPAddress Address, int Port)
+{
+    public EndpointKey(IPEndPoint endpoint)
+        : this(endpoint.Address, endpoint.Port)
+    {
+    }
+}
+
+// Bounded per-session endpoint bond state used for received proofs and pending bonding pings.
+internal struct EndpointBondTable
+{
+    public const int Capacity = 16;
+
+    private Entry[]? _entries;
+    private int _count;
+
+    public readonly int Count => _count;
+    public readonly bool IsEmpty => _count == 0;
+
+    public bool Record(EndpointKey endpoint, long stamp)
+    {
+        Entry[] entries = _entries ??= new Entry[Capacity];
+        for (int i = 0; i < _count; i++)
+        {
+            if (entries[i].Endpoint.Equals(endpoint))
+            {
+                entries[i] = new(endpoint, stamp);
+                return false;
+            }
+        }
+
+        if (_count < entries.Length)
+        {
+            entries[_count++] = new(endpoint, stamp);
+            return false;
+        }
+
+        entries[LowestStampIndex(entries)] = new(endpoint, stamp);
+        return true;
+    }
+
+    public bool Remove(EndpointKey endpoint, long expectedStamp)
+    {
+        Entry[]? entries = _entries;
+        if (entries is null) return false;
+
+        for (int i = 0; i < _count; i++)
+        {
+            if (entries[i].Endpoint.Equals(endpoint) && entries[i].Stamp == expectedStamp)
+            {
+                RemoveAt(entries, i);
+                return true;
+            }
+        }
+
+        return false;
+    }
+
+    public readonly bool Contains(EndpointKey endpoint)
+    {
+        Entry[]? entries = _entries;
+        if (entries is null) return false;
+
+        for (int i = 0; i < _count; i++)
+        {
+            if (entries[i].Endpoint.Equals(endpoint))
+            {
+                return true;
+            }
+        }
+
+        return false;
+    }
+
+    public readonly bool HasFresh(EndpointKey endpoint, long minValidStamp)
+    {
+        Entry[]? entries = _entries;
+        if (entries is null) return false;
+
+        for (int i = 0; i < _count; i++)
+        {
+            Entry entry = entries[i];
+            if (entry.Endpoint.Equals(endpoint) && entry.Stamp > minValidStamp)
+            {
+                return true;
+            }
+        }
+
+        return false;
+    }
+
+    public void PruneStale(long minValidStamp)
+    {
+        Entry[]? entries = _entries;
+        if (entries is null) return;
+
+        int i = 0;
+        while (i < _count)
+        {
+            if (entries[i].Stamp > minValidStamp)
+            {
+                i++;
+                continue;
+            }
+
+            RemoveAt(entries, i);
+        }
+    }
+
+    private void RemoveAt(Entry[] entries, int index)
+    {
+        _count--;
+        entries[index] = entries[_count];
+        entries[_count] = default;
+    }
+
+    private static int LowestStampIndex(Entry[] entries)
+    {
+        int lowestIndex = 0;
+        long lowestStamp = entries[0].Stamp;
+        for (int i = 1; i < entries.Length; i++)
+        {
+            if (entries[i].Stamp >= lowestStamp) continue;
+
+            lowestIndex = i;
+            lowestStamp = entries[i].Stamp;
+        }
+
+        return lowestIndex;
+    }
+
+    private readonly record struct Entry(EndpointKey Endpoint, long Stamp);
+}
```

### src/Nethermind/Nethermind.Network.Discovery/Discv4/Kademlia/KademliaAdapter.cs
```diff
@@ -1,6 +1,7 @@
 // SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
 // SPDX-License-Identifier: LGPL-3.0-only
 
+using System.Net;
 using Nethermind.Config;
 using Nethermind.Core;
 using Nethermind.Core.Caching;
@@ -37,7 +38,8 @@ ILogManager logManager
     private readonly TimeSpan _expirationTime = TimeSpan.FromMilliseconds(discoveryConfig.MessageExpiryTime);
     private readonly TimeSpan _waitAfterPongDelay = TimeSpan.FromMilliseconds(discoveryConfig.BondWaitTime);
 
-    private readonly RateLimiter _outboundRateLimiter = new(discoveryConfig.MaxOutgoingMessagePerSecond);
+    private readonly RateLimiter _outboundRateLimiter = new(Math.Max(1, discoveryConfig.MaxOutgoingMessagePerSecond / 2));
+    private readonly RateLimiter _responseRateLimiter = new(Math.Max(1, discoveryConfig.MaxOutgoingMessagePerSecond / 2));
     public IMsgSender? MsgSender { get; set; }
 
     private readonly ConcurrentDictionary<(ValueHash256, MsgType), IMessageHandler[]> _incomingMessageHandlers = new();
@@ -50,8 +52,8 @@ public NodeSession GetSession(Node node) => _sessions.SetOrGet(
 
     private async Task<bool> EnsureOutgoingMessageBondedPeer(Node node, NodeSession nodeSession, CancellationToken token)
     {
-        // If we have received ping, then we have ponged which mean we should be bonded from their point of view
-        if (nodeSession is { HasReceivedPing: true, NotTooManyFailure: true }) return true;
+        // If we received a ping from this endpoint, our pong should have bonded us from their point of view.
+        if (nodeSession.NotTooManyFailure && nodeSession.HasReceivedPingFrom(node.Address)) return true;
 
         if (Logger.IsTrace) Logger.Trace($"Ensure session for node {node}");
         if (!await Ping(node, token)) return false;
@@ -176,11 +178,12 @@ CancellationToken token
     }
 
 
-    private async Task SendMessage(NodeSession session, DiscoveryMsg msg, CancellationToken token)
+    private async Task SendMessage(NodeSession session, DiscoveryMsg msg, CancellationToken token, bool isResponse = false)
     {
         if (MsgSender is { } sender)
         {
-            await _outboundRateLimiter.WaitAsync(token);
+            await (isResponse ? _responseRateLimiter : _outboundRateLimiter).WaitAsync(token);
+
             session.RecordStatsForOutgoingMsg(msg);
             await sender.SendMsg(msg);
         }
@@ -196,13 +199,23 @@ public async Task<bool> Ping(Node receiver, CancellationToken token)
         {
             EnrSequence = (await nodeRecordProvider.GetCurrentAsync(token)).EnrSequence // optional and does not seem to be used anywhere.
         };
-        session.OnPingSent();
-        DiscoveryResponse<PongMsg> response = await CallAndWaitForResponse(MsgType.Pong, new PongMsgHandler(msg), receiver, session, msg, _pingTimeout, token);
-        if (!response.HasResponse) return false;
+        long pingToken = session.OnPingSent(receiver.Address);
+        try
+        {
+            DiscoveryResponse<PongMsg> response = await CallAndWaitForResponse(MsgType.Pong, new PongMsgHandler(msg), receiver, session, msg, _pingTimeout, token);
+            if (!response.HasResponse) return false;
+            if (response.Value.FarAddress is not { } pongEndpoint) return false;
 
-        session.OnPongReceived(response.Value.FarAddress ?? receiver.Address);
-        await RefreshRemoteRecordIfNewer(receiver, response.Value.EnrSequence, token);
-        return true;
+            session.OnPongReceived(pongEndpoint);
+            if (!session.HasEndpointBond(receiver.Address)) return false;
+
+            await RefreshRemoteRecordIfNewer(receiver, response.Value.EnrSequence, token);
+            return true;
+        }
+        finally
+        {
+            session.OnPingCompleted(receiver.Address, pingToken);
+        }
     }
 
     public async Task<Node[]?> FindNeighbours(Node receiver, PublicKey target, CancellationToken token)
@@ -250,9 +263,11 @@ protected override void AddOrRefreshRemoteNode(Node node)
 
     private async Task<bool> HandleEnrRequest(Node node, NodeSession session, EnrRequestMsg msg, CancellationToken token)
     {
-        if (!session.HasEndpointProof(node.Address))
+        await WaitForPendingEndpointBond(node.Address, session, token);
+
+        if (!session.HasEndpointBond(node.Address))
         {
-            if (Logger.IsDebug) Logger.Debug($"Rejecting enr request from unbonded peer {node}");
+            if (Logger.IsDebug) Logger.Debug($"Rejecting enr request from unbonded endpoint {node.Address} for peer {node.Id}");
             return false;
         }
 
@@ -262,35 +277,45 @@ private async Task<bool> HandleEnrRequest(Node node, NodeSession session, EnrReq
             return false;
         }
 
-        await SendMessage(session, new EnrResponseMsg(node.Address, await nodeRecordProvider.GetCurrentAsync(token), new Hash256(requestHash)), token);
+        await SendMessage(session, new EnrResponseMsg(node.Address, await nodeRecordProvider.GetCurrentAsync(token), new Hash256(requestHash)), token, isResponse: true);
         return true;
     }
 
     private async Task<bool> HandleFindNode(Node node, NodeSession session, FindNodeMsg msg, CancellationToken token)
     {
-        if (!session.HasEndpointProof(node.Address))
+        await WaitForPendingEndpointBond(node.Address, session, token);
+
+        if (!session.HasEndpointBond(node.Address))
         {
-            if (Logger.IsDebug) Logger.Debug($"Rejecting findNode request from unbonded peer {node}");
+            if (Logger.IsDebug) Logger.Debug($"Rejecting findNode request from unbonded endpoint {node.Address} for peer {node.Id}");
             return false;
         }
 
         PublicKey publicKey = new(msg.SearchedNodeId);
         Node[] nodes = kademlia.Value.GetKNeighbour(publicKey, node, false);
         if (nodes.Length == 0)
         {
-            await SendMessage(session, new NeighborsMsg(node.Address, CalculateExpirationTime(), nodes), token);
+            await SendMessage(session, new NeighborsMsg(node.Address, CalculateExpirationTime(), nodes), token, isResponse: true);
             return true;
         }
 
         for (int i = 0; i < nodes.Length; i += MaxNodesPerNeighborsMsg)
         {
             int batchEnd = Math.Min(i + MaxNodesPerNeighborsMsg, nodes.Length);
-            await SendMessage(session, new NeighborsMsg(node.Address, CalculateExpirationTime(), new ArraySegment<Node>(nodes, i, batchEnd - i)), token);
+            await SendMessage(session, new NeighborsMsg(node.Address, CalculateExpirationTime(), new ArraySegment<Node>(nodes, i, batchEnd - i)), token, isResponse: true);
         }
 
         return true;
     }
 
+    private async ValueTask WaitForPendingEndpointBond(IPEndPoint endpoint, NodeSession session, CancellationToken token)
+    {
+        if (!session.HasEndpointBond(endpoint) && session.HasReceivedPingFrom(endpoint) && session.HasPendingBondingPing(endpoint))
+        {
+            await session.WaitForEndpointBond(endpoint, _pingTimeout, token);
+        }
+    }
+
     private async Task HandlePing(Node node, NodeSession session, PingMsg ping, CancellationToken token)
     {
         if (Logger.IsTrace) Logger.Trace($"Receive ping from {node}");
@@ -301,13 +326,16 @@ private async Task HandlePing(Node node, NodeSession session, PingMsg ping, Canc
         }
 
         PongMsg msg = new(ping.FarAddress!, CalculateExpirationTime(), pingMdc, (await nodeRecordProvider.GetCurrentAsync(token)).EnrSequence);
-        session.OnPingReceived();
-        await SendMessage(session, msg, token);
-        await RefreshRemoteRecordIfNewer(node, ping.EnrSequence, token);
+        session.OnPingReceived(node.Address);
+        await SendMessage(session, msg, token, isResponse: true);
+        if (session.HasEndpointBond(node.Address))
+        {
+            await RefreshRemoteRecordIfNewer(node, ping.EnrSequence, token);
+        }
 
-        if (!session.HasReceivedPong)
+        if (!session.HasEndpointBond(node.Address))
         {
-            // If we have never received any pong, then this peer is not bonded and we should not respond to any auth request.
+            // If this endpoint has no recent pong, it is not bonded and we should not respond to auth requests.
             // Send a ping to bond the peer.
             _ = await Ping(node, token);
         }
```

### src/Nethermind/Nethermind.Network.Discovery/Discv4/NodeSession.cs
```diff
@@ -1,4 +1,4 @@
-// SPDX-FileCopyrightText: 2025 Demerzel Solutions Limited
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using System.Net;
@@ -16,28 +16,98 @@ public sealed record NodeSession(INodeStats NodeStats, ITimestamper Timestamper)
     public const int AuthenticatedRequestFailureLimit = 5;
 
     private int _authenticatedRequestFailureCount;
-    private long _lastPongReceivedTicks;
-    private long _lastPingReceivedTicks;
     private long _lastPingSentTicks;
-    private IPEndPoint? _lastPongEndpoint;
+    private long _lastPingToken;
+    private readonly Lock _endpointBondLock = new();
+    private EndpointBondTable _receivedPings;
+    private EndpointBondTable _receivedPongs;
+    private EndpointBondTable _pendingBondingPings;
+    private TaskCompletionSource? _endpointBondChanged;
 
-    public bool HasReceivedPing => Volatile.Read(ref _lastPingReceivedTicks) + BondTimeout.Ticks > Timestamper.UtcNow.Ticks;
     public bool NotTooManyFailure => Volatile.Read(ref _authenticatedRequestFailureCount) <= AuthenticatedRequestFailureLimit;
-    public bool HasReceivedPong => Volatile.Read(ref _lastPongReceivedTicks) + BondTimeout.Ticks > Timestamper.UtcNow.Ticks;
     public bool HasTriedPingRecently => Volatile.Read(ref _lastPingSentTicks) + PingRetryTimeout.Ticks > Timestamper.UtcNow.Ticks;
-    public bool HasEndpointProof(IPEndPoint endpoint) =>
-        HasReceivedPong && Volatile.Read(ref _lastPongEndpoint) is { } lastPongEndpoint && lastPongEndpoint.Equals(endpoint);
+
+    public bool HasReceivedPing
+    {
+        get
+        {
+            lock (_endpointBondLock)
+            {
+                _receivedPings.PruneStale(StaleBondStamp);
+                return !_receivedPings.IsEmpty;
+            }
+        }
+    }
+
+    public bool HasReceivedPong
+    {
+        get
+        {
+            lock (_endpointBondLock)
+            {
+                _receivedPongs.PruneStale(StaleBondStamp);
+                return !_receivedPongs.IsEmpty;
+            }
+        }
+    }
+
+    public bool HasReceivedPingFrom(IPEndPoint endpoint)
+    {
+        EndpointKey endpointKey = new(endpoint);
+        lock (_endpointBondLock)
+        {
+            long minValidStamp = StaleBondStamp;
+            _receivedPings.PruneStale(minValidStamp);
+            return _receivedPings.HasFresh(endpointKey, minValidStamp);
+        }
+    }
+
+    public bool HasEndpointBond(IPEndPoint endpoint)
+    {
+        EndpointKey endpointKey = new(endpoint);
+        lock (_endpointBondLock)
+        {
+            long minValidStamp = StaleBondStamp;
+            _receivedPongs.PruneStale(minValidStamp);
+            return _receivedPongs.HasFresh(endpointKey, minValidStamp);
+        }
+    }
+
+    public bool HasPendingBondingPing(IPEndPoint endpoint)
+    {
+        EndpointKey endpointKey = new(endpoint);
+        lock (_endpointBondLock)
+        {
+            return _pendingBondingPings.Contains(endpointKey);
+        }
+    }
 
     public void ResetAuthenticatedRequestFailure() => Interlocked.Exchange(ref _authenticatedRequestFailureCount, 0);
     public void OnAuthenticatedRequestFailure() => Interlocked.Increment(ref _authenticatedRequestFailureCount);
 
     public void OnPongReceived(IPEndPoint endpoint)
     {
-        Volatile.Write(ref _lastPongEndpoint, endpoint);
-        Volatile.Write(ref _lastPongReceivedTicks, Timestamper.UtcNow.Ticks);
+        EndpointKey endpointKey = new(endpoint);
+        lock (_endpointBondLock)
+        {
+            long nowTicks = Timestamper.UtcNow.Ticks;
+            _receivedPongs.PruneStale(nowTicks - BondTimeout.Ticks);
+            _receivedPongs.Record(endpointKey, nowTicks);
+        }
+
+        SignalEndpointBondChanged();
     }
 
-    public void OnPingReceived() => Volatile.Write(ref _lastPingReceivedTicks, Timestamper.UtcNow.Ticks);
+    public void OnPingReceived(IPEndPoint endpoint)
+    {
+        EndpointKey endpointKey = new(endpoint);
+        lock (_endpointBondLock)
+        {
+            long nowTicks = Timestamper.UtcNow.Ticks;
+            _receivedPings.PruneStale(nowTicks - BondTimeout.Ticks);
+            _receivedPings.Record(endpointKey, nowTicks);
+        }
+    }
 
     public void RecordStatsForOutgoingMsg(DiscoveryMsg msg) => RecordStatsForMsg(msg, outgoing: true);
     public void RecordStatsForIncomingMsg(DiscoveryMsg msg) => RecordStatsForMsg(msg, outgoing: false);
@@ -61,4 +131,91 @@ private void RecordStatsForMsg(DiscoveryMsg msg, bool outgoing)
     }
 
     public void OnPingSent() => Volatile.Write(ref _lastPingSentTicks, Timestamper.UtcNow.Ticks);
+
+    public long OnPingSent(IPEndPoint endpoint)
+    {
+        OnPingSent();
+        long token = Interlocked.Increment(ref _lastPingToken);
+        EndpointKey endpointKey = new(endpoint);
+        bool evicted;
+        lock (_endpointBondLock)
+        {
+            evicted = _pendingBondingPings.Record(endpointKey, token);
+        }
+
+        // An eviction drops another endpoint's pending ping, so wake its waiter to return false instead of timing out.
+        if (evicted)
+        {
+            SignalEndpointBondChanged();
+        }
+
+        return token;
+    }
+
+    public void OnPingCompleted(IPEndPoint endpoint, long token)
+    {
+        EndpointKey endpointKey = new(endpoint);
+        bool removed;
+        lock (_endpointBondLock)
+        {
+            removed = _pendingBondingPings.Remove(endpointKey, token);
+        }
+
+        if (removed)
+        {
+            SignalEndpointBondChanged();
+        }
+    }
+
+    public async ValueTask<bool> WaitForEndpointBond(IPEndPoint endpoint, TimeSpan timeout, CancellationToken token)
+    {
+        using CancellationTokenSource timeoutCts = new(timeout);
+        using CancellationTokenSource waitCts = CancellationTokenSource.CreateLinkedTokenSource(token, timeoutCts.Token);
+
+        EndpointKey endpointKey = new(endpoint);
+        while (true)
+        {
+            Task bondChanged;
+            lock (_endpointBondLock)
+            {
+                long minValidStamp = StaleBondStamp;
+                _receivedPongs.PruneStale(minValidStamp);
+                if (_receivedPongs.HasFresh(endpointKey, minValidStamp))
+                {
+                    return true;
+                }
+
+                if (!_pendingBondingPings.Contains(endpointKey))
+                {
+                    return false;
+                }
+
+                bondChanged = (_endpointBondChanged ??= new(TaskCreationOptions.RunContinuationsAsynchronously)).Task;
+            }
+
+            try
+            {
+                await bondChanged.WaitAsync(waitCts.Token);
+            }
+            catch (OperationCanceledException) when (!token.IsCancellationRequested && timeoutCts.IsCancellationRequested)
+            {
+                return HasEndpointBond(endpoint);
+            }
+        }
+    }
+
+    private void SignalEndpointBondChanged()
+    {
+        TaskCompletionSource? completion;
+        lock (_endpointBondLock)
+        {
+            completion = _endpointBondChanged;
+            _endpointBondChanged = null;
+        }
+
+        completion?.TrySetResult();
+    }
+
+    // Endpoint stamps recorded at or before this tick predate the bond window and are treated as expired.
+    private long StaleBondStamp => Timestamper.UtcNow.Ticks - BondTimeout.Ticks;
 }
```

### src/Nethermind/Nethermind.Network.Discovery/Discv5/DiscoveryV5App.cs
```diff
@@ -51,7 +51,8 @@ public DiscoveryV5App(
         IPAddress externalIp = enode.HostIp;
         _allowNonRoutableEnrs = ShouldAcceptNonRoutableEnrs(externalIp);
 
-        List<Node> bootNodes = CreateBootNodes(networkConfig, discoveryConfig);
+        bool useDefaultBootnodes = ShouldUseDefaultDiscv5Bootnodes(externalIp, discoveryConfig);
+        List<Node> bootNodes = CreateBootNodes(networkConfig, discoveryConfig, useDefaultBootnodes);
         ITimestamper timestamper = rootScope.ResolveOptional<ITimestamper>() ?? Timestamper.Default;
 
         _discv5Services = rootScope.BeginLifetimeScope(builder =>
@@ -87,6 +88,9 @@ Func<NettyDiscoveryV5Handler> NettyDiscoveryHandlerFactory
     }
 
     internal List<Node> CreateBootNodes(INetworkConfig networkConfig, IDiscoveryConfig discoveryConfig)
+        => CreateBootNodes(networkConfig, discoveryConfig, discoveryConfig.UseDefaultDiscv5Bootnodes);
+
+    private List<Node> CreateBootNodes(INetworkConfig networkConfig, IDiscoveryConfig discoveryConfig, bool useDefaultBootnodes)
     {
         List<Node> bootNodes = [];
         using PooledSet<Hash256> seen = new(networkConfig.Bootnodes.Length);
@@ -99,7 +103,7 @@ internal List<Node> CreateBootNodes(INetworkConfig networkConfig, IDiscoveryConf
             configuredStats.Record(AddBootNode(bootNodes, seen, configuredBootnodes[i]));
         }
 
-        if (discoveryConfig.UseDefaultDiscv5Bootnodes)
+        if (useDefaultBootnodes)
         {
             string[] defaultBootnodes = GetDefaultBootnodes();
             for (int i = 0; i < defaultBootnodes.Length; i++)
@@ -110,7 +114,7 @@ internal List<Node> CreateBootNodes(INetworkConfig networkConfig, IDiscoveryConf
 
         if (Logger.IsInfo)
         {
-            Logger.Info($"Discv5 bootnodes accepted: {bootNodes.Count} ({configuredStats.Added}/{configuredStats.Total} configured, {defaultStats.Added}/{defaultStats.Total} default, duplicates: {configuredStats.Duplicates + defaultStats.Duplicates}, skipped: {configuredStats.Skipped + defaultStats.Skipped}, use default discv5 bootnodes: {discoveryConfig.UseDefaultDiscv5Bootnodes}).");
+            Logger.Info($"Discv5 bootnodes accepted: {bootNodes.Count} ({configuredStats.Added}/{configuredStats.Total} configured, {defaultStats.Added}/{defaultStats.Total} default, duplicates: {configuredStats.Duplicates + defaultStats.Duplicates}, skipped: {configuredStats.Skipped + defaultStats.Skipped}, use default discv5 bootnodes: {useDefaultBootnodes}).");
         }
 
         if (bootNodes.Count == 0 && Logger.IsWarn)
@@ -228,8 +232,15 @@ internal static bool IsDiscoveryAddressRoutable(IPAddress ipAddress)
     internal static bool IsConsensusOnlyNodeRecord(NodeRecord enr)
         => enr.HasEntry(EnrContentKey.Eth2) && !enr.HasEntry(EnrContentKey.Eth);
 
+    internal static bool ShouldUseDefaultDiscv5Bootnodes(IPAddress externalIp, IDiscoveryConfig discoveryConfig)
+        => discoveryConfig.UseDefaultDiscv5Bootnodes && !IsKnownPrivateDiscoveryAddress(externalIp);
+
     private static bool ShouldAcceptNonRoutableEnrs(IPAddress externalIp)
+        => IsKnownPrivateDiscoveryAddress(externalIp);
+
+    private static bool IsKnownPrivateDiscoveryAddress(IPAddress externalIp)
         => !IPAddress.Any.Equals(externalIp)
+            && !IPAddress.IPv6Any.Equals(externalIp)
             && !IPAddress.None.Equals(externalIp)
             && externalIp.IsLoopbackOrPrivateOrLinkLocal;
 
```

### src/Nethermind/Nethermind.Network.Discovery/Discv5/Kademlia/KademliaAdapter.cs
```diff
@@ -53,6 +53,7 @@ public sealed class KademliaAdapter(
     private readonly TimeSpan _findNodeTimeout = TimeSpan.FromMilliseconds(discoveryConfig.SendNodeTimeout);
     private readonly IKademliaDistance<Hash256> _distance = distance;
     private readonly Hash256 _currentNodeHash = kademliaConfig.CurrentNodeId.Id.Hash;
+    private readonly int _bucketSize = kademliaConfig.KSize;
     private readonly DisposingLruCache<SessionKey, Session> _sessions = new(MaxSessions, "discv5 sessions");
     private readonly LruCache<ChallengeKey, SentChallenge> _sentChallenges = new(MaxSentChallenges, "discv5 sent challenges");
     private readonly Queue<SentChallengeExpiry> _sentChallengeExpiries = new();
@@ -114,7 +115,7 @@ public async Task<bool> Ping(Node receiver, CancellationToken token)
         }
 
         if (Logger.IsTrace) Logger.Trace($"Discv5 PING {ping.RequestId} to {receiver:s} succeeded.");
-        kademlia.Value.AddOrRefresh(receiver);
+        AddOrRefreshLiveNode(receiver);
         await RefreshRemoteRecordIfNewer(receiver, responseHandler.EnrSequence, token);
         return true;
     }
@@ -499,13 +500,23 @@ private async Task SendWhoAreYou(IPEndPoint endpoint, Packet requestPacket, Valu
             return;
         }
 
-        ulong enrSequence = TryGetKnownSignedRecord(nodeId, out NodeRecord? record) ? record.EnrSequence : 0UL;
+        ulong enrSequence = GetChallengeEnrSequence(nodeId, endpoint);
         byte[] packet = packetCodec.EncodeWhoAreYou(nodeId.Bytes, requestPacket.Nonce.Span, enrSequence);
         SetSentChallenge(challengeKey, packet);
         if (Logger.IsTrace) Logger.Trace($"Sending discv5 WHOAREYOU challenge to {endpoint}, known ENR seq: {enrSequence}, bytes: {packet.Length}.");
         await discoveryHandler.SendAsync(packet, endpoint, token);
     }
 
+    private ulong GetChallengeEnrSequence(ValueHash256 nodeId, IPEndPoint endpoint)
+    {
+        if (!TryGetKnownSignedRecord(nodeId, out NodeRecord? record))
+        {
+            return 0UL;
+        }
+
+        return HasDiscoveryEndpoint(record, endpoint) ? record.EnrSequence : 0UL;
+    }
+
     private async Task HandleHandshakeMessage(
         IPEndPoint endpoint,
         ValueHash256 nodeId,
@@ -587,7 +598,6 @@ private async Task HandleMessage(PublicKey remotePublicKey, IPEndPoint endpoint,
                 break;
             case FindNodeMsg findNode:
                 await HandleFindNode(remoteNode, findNode, token);
-                kademlia.Value.AddOrRefresh(remoteNode);
                 break;
             case TalkReqMsg talkReq:
                 using (TalkRespMsg talkResp = new(talkReq.RequestId, ReadOnlyMemory<byte>.Empty))
@@ -628,6 +638,60 @@ private async Task RunRemoteRecordRefresh(Node node, ulong advertisedSequence, C
     protected override void AddOrRefreshRemoteNode(Node node)
         => kademlia.Value.AddOrRefresh(node);
 
+    private void AddOrRefreshLiveNode(Node node)
+    {
+        IKademlia<PublicKey, Node> table = kademlia.Value;
+        if (node.ValidatedProtocol == true)
+        {
+            int distance = _distance.CalculateLogDistance(_currentNodeHash, node.Id.Hash);
+            // Removing a stale bucket entry may promote an unvalidated replacement, so keep evicting until the
+            // endpoint-validated node can be admitted or no stale, non-static entries remain at this distance.
+            while (true)
+            {
+                Node[] nodes = table.GetAllAtDistance(distance);
+                if (nodes.Length < _bucketSize || ContainsNode(nodes, node))
+                {
+                    break;
+                }
+
+                if (!TryRemoveStaleNonStaticNode(table, nodes))
+                {
+                    break;
+                }
+            }
+        }
+
+        table.AddOrRefresh(node);
+    }
+
+    private static bool TryRemoveStaleNonStaticNode(IKademlia<PublicKey, Node> table, Node[] nodes)
+    {
+        for (int i = nodes.Length - 1; i >= 0; i--)
+        {
+            Node candidate = nodes[i];
+            if (!candidate.IsStatic && candidate.ValidatedProtocol != true)
+            {
+                table.Remove(candidate);
+                return true;
+            }
+        }
+
+        return false;
+    }
+
+    private static bool ContainsNode(Node[] nodes, Node node)
+    {
+        for (int i = 0; i < nodes.Length; i++)
+        {
+            if (nodes[i].Id.Equals(node.Id))
+            {
+                return true;
+            }
+        }
+
+        return false;
+    }
+
     private bool HandleResponse(ValueHash256 nodeId, Discv5Message message)
     {
         ResponseKey responseKey = new(nodeId, message.RequestId, message.MessageType);
@@ -702,10 +766,27 @@ private void AddFindNodeRecordsAtDistance(
     {
         Node[] nodes = kademlia.Value.GetAllAtDistance(distance);
         Hash256 requesterHash = requester.IdHash;
+        AddFindNodeRecords(nodes, requesterHash, allowNonRoutableRelays, seen, ref result, onlyValidated: true);
+        AddFindNodeRecords(nodes, requesterHash, allowNonRoutableRelays, seen, ref result, onlyValidated: false);
+    }
+
+    private void AddFindNodeRecords(
+        Node[] nodes,
+        Hash256 requesterHash,
+        bool allowNonRoutableRelays,
+        PooledSet<Hash256> seen,
+        ref ArrayPoolListRef<NodeRecord> result,
+        bool onlyValidated)
+    {
         for (int i = 0; i < nodes.Length && result.Count < MaxFindNodeRecords; i++)
         {
             Node node = nodes[i];
 
+            if ((node.ValidatedProtocol == true) != onlyValidated)
+            {
+                continue;
+            }
+
             if (node.IdHash.Equals(requesterHash) || node.Enr is not { Signature: not null } || !seen.Add(node.Id.Hash))
             {
                 continue;
@@ -822,6 +903,9 @@ internal static bool IsAcceptableNodeRecord(NodeRecord record, ValueHash256 expe
             node.Id.Hash == expectedNodeId &&
             DiscoveryV5App.IsDiscoveryAddressAcceptable(node.Address.Address, allowNonRoutable);
 
+    internal static bool HasDiscoveryEndpoint(NodeRecord record, IPEndPoint endpoint)
+        => record.DiscoveryPort == endpoint.Port && record.DiscoveryIp?.Equals(endpoint.Address) == true;
+
     internal static bool HasExpectedNodeId(NodeRecord record, ValueHash256 expectedNodeId)
         => record.GetObj<CompressedPublicKey>(EnrContentKey.SecP256k1)?.Decompress().Hash == expectedNodeId;
 
```
