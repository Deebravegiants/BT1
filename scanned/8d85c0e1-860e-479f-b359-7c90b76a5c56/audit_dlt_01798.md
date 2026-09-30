# [?] Fix handleLCL consensus bug:

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2017-03-24
Source: https://github.com/XRPLF/rippled/commit/2449f9c18d8f4e9c0e864e809c977cb0fe0feca0
Type: security-commit

## Details
Fix handleLCL consensus bug:

Consensus::checkLCL can change state_ but it was being called inside
timerEntry after a switch on the current state_.  In rare cases, this might
end up calling stateEstablish even when the state_ was open.

## Patch
### src/ripple/consensus/Consensus.h
```diff
@@ -867,15 +867,18 @@ Consensus<Derived, Traits>::timerEntry (NetClock::time_point const& now)
     {
         using namespace std::chrono;
 
+        // checkLCL may change state_, so it needs to run prior to the
+        // switch (state_) below
+        if(state_ == State::open || state_ == State::establish)
+            checkLCL ();
+
         switch (state_)
         {
         case State::open:
-            checkLCL ();
             statePreClose ();
             break;
 
         case State::establish:
-            checkLCL ();
             stateEstablish ();
             break;
 
```

### src/test/consensus/Consensus_test.cpp
```diff
@@ -93,7 +93,7 @@ class Consensus_test : public beast::unit_test::suite
         using namespace std::chrono;
 
         // Run two tests
-        //  1. The slow peer is participating inconsensus
+        //  1. The slow peer is participating in consensus
         //  2. The slow peer is just observing
 
         for(auto isParticipant : {true, false})
@@ -295,6 +295,43 @@ class Consensus_test : public beast::unit_test::suite
 
         }
 
+        // Additional test engineered to switch LCL during the establish phase.
+        // This was added to trigger a scenario that previously crashed, in which
+        // switchLCL switched from establish to open phase, but still processed
+        // the establish phase logic.
+        {
+          using namespace csf;
+          using namespace std::chrono;
+
+          // A mostly disjoint topology
+          std::vector<UNL> unls;
+          unls.push_back({0, 1});
+          unls.push_back({2});
+          unls.push_back({3});
+          unls.push_back({0, 1, 2, 3, 4});
+          std::vector<int> membership = {0, 0, 1, 2, 3};
+
+          TrustGraph tg{unls, membership};
+
+          Sim sim(tg, topology(tg, fixed{round<milliseconds>(
+                                       0.2 * LEDGER_GRANULARITY)}));
+
+          // initial ground to set prior state
+          sim.run(1);
+          for (auto &p : sim.peers) {
+            // A long delay to acquire a missing ledger from the network
+            p.missingLedgerDelay = 2 * LEDGER_MIN_CLOSE;
+
+            // Everyone sees only their own LCL
+            p.openTxs.insert(Tx(p.id));
+          }
+          // additional rounds to generate wrongLCL and recover
+          sim.run(2);
+
+          // Check all peers recovered
+          for (auto &p : sim.peers)
+            BEAST_EXPECT(p.LCL() == sim.peers[0].LCL());
+        }
     }
 
     void
```
