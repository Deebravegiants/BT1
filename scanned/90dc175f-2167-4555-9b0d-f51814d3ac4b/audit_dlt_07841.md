# [?] attempt to fix flakness on possible race condition (#10490)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2026-03-16
Source: https://github.com/Consensys-Incorporated/teku/commit/7f63fbf92cd9195f52585e15d30f6e75ed8a6323
Type: security-commit

## Details
attempt to fix flakness on possible race condition (#10490)

Signed-off-by: Gabriel Fukushima <gabrielfukushima@gmail.com>

## Patch
### networking/eth2/src/integration-test/java/tech/pegasys/teku/networking/eth2/BeaconBlocksByRangeIntegrationTest.java
```diff
@@ -72,7 +72,7 @@ public void shouldSendEmptyResponseWhenCountIsZero() throws Exception {
     final List<SignedBeaconBlock> blocks = new ArrayList<>();
     waitFor(
         peer.requestBlocksByRange(UInt64.ONE, UInt64.ZERO, RpcResponseListener.from(blocks::add)));
-    assertThat(peer.getOutstandingRequests()).isEqualTo(0);
+    waitFor(() -> assertThat(peer.getOutstandingRequests()).isEqualTo(0));
     assertThat(blocks).isEmpty();
   }
 
@@ -229,7 +229,7 @@ public void requestBlockByRange_withDisparateVersionsEnabled_requestNextSpecBloc
             block1.getSlot(), UInt64.valueOf(2), RpcResponseListener.from(blocks::add));
 
     waitFor(() -> assertThat(res).isDone());
-    assertThat(peer.getOutstandingRequests()).isEqualTo(0);
+    waitFor(() -> assertThat(peer.getOutstandingRequests()).isEqualTo(0));
 
     if (nextSpecEnabledLocally && nextSpecEnabledRemotely) {
       // We should receive a successful response
@@ -270,7 +270,7 @@ private List<SignedBeaconBlock> requestBlocksByRange(final Eth2Peer peer)
     waitFor(
         peer.requestBlocksByRange(
             UInt64.ONE, UInt64.valueOf(10), RpcResponseListener.from(blocks::add)));
-    assertThat(peer.getOutstandingRequests()).isEqualTo(0);
+    waitFor(() -> assertThat(peer.getOutstandingRequests()).isEqualTo(0));
     return blocks;
   }
 }
```
