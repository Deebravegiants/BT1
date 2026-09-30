# [?] net: fix use-after-free in tests

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-03-18
Source: https://github.com/litecoin-project/litecoin/commit/7d8e1dec3b26074df1533f715871f79c956cc224
Type: security-commit

## Details
net: fix use-after-free in tests

In PeerLogicValidation::PeerLogicValidation() we would schedule a lambda
function to execute later, capturing the local variable
`consensusParams` by reference.

Presumably this was considered safe because `consensusParams` is a
reference itself to a global variable which is not supposed to change,
but it can in tests.

Fixes https://github.com/bitcoin/bitcoin/issues/18372

## Patch
### src/net_processing.cpp
```diff
@@ -1127,7 +1127,7 @@ PeerLogicValidation::PeerLogicValidation(CConnman* connmanIn, BanMan* banman, CS
     // combine them in one function and schedule at the quicker (peer-eviction)
     // timer.
     static_assert(EXTRA_PEER_CHECK_INTERVAL < STALE_CHECK_INTERVAL, "peer eviction timer should be less than stale tip check timer");
-    scheduler.scheduleEvery([&] { this->CheckForStaleTipAndEvictPeers(consensusParams); }, std::chrono::seconds{EXTRA_PEER_CHECK_INTERVAL});
+    scheduler.scheduleEvery([this, consensusParams] { this->CheckForStaleTipAndEvictPeers(consensusParams); }, std::chrono::seconds{EXTRA_PEER_CHECK_INTERVAL});
 }
 
 /**
```
