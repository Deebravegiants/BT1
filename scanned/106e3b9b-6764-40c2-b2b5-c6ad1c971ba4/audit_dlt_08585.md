# [?] Fix crash in Slot::deletePeer (#5635)

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2025-07-31
Source: https://github.com/XRPLF/rippled/commit/d835e974905474d6b7d90be9f846c4cb2abe180b
Type: security-commit

## Details
Fix crash in Slot::deletePeer (#5635)

Fix crash due to recurrent call to `Slot::deletePeer` (via `OverlayImpl::unsquelch`) when a peer is disconnected at just the wrong moment.

## Patch
### src/xrpld/overlay/Slot.h
```diff
@@ -446,6 +446,8 @@ Slot<clock_type>::deletePeer(PublicKey const& validator, id_t id, bool erase)
     auto it = peers_.find(id);
     if (it != peers_.end())
     {
+        std::vector<Peer::id_t> toUnsquelch;
+
         JLOG(journal_.trace())
             << "deletePeer: " << Slice(validator) << " " << id << " selected "
             << (it->second.state == PeerState::Selected) << " considered "
@@ -457,7 +459,7 @@ Slot<clock_type>::deletePeer(PublicKey const& validator, id_t id, bool erase)
             for (auto& [k, v] : peers_)
             {
                 if (v.state == PeerState::Squelched)
-                    handler_.unsquelch(validator, k);
+                    toUnsquelch.push_back(k);
                 v.state = PeerState::Counting;
                 v.count = 0;
                 v.expire = now;
@@ -479,6 +481,10 @@ Slot<clock_type>::deletePeer(PublicKey const& validator, id_t id, bool erase)
 
         if (erase)
             peers_.erase(it);
+
+        // Must be after peers_.erase(it)
+        for (auto const& k : toUnsquelch)
+            handler_.unsquelch(validator, k);
     }
 }
 
```

### src/xrpld/overlay/detail/OverlayImpl.cpp
```diff
@@ -1423,7 +1423,12 @@ OverlayImpl::updateSlotAndSquelch(
     if (!strand_.running_in_this_thread())
         return post(
             strand_,
-            [this, key, validator, peers = std::move(peers), type]() mutable {
+            // Must capture copies of reference parameters (i.e. key, validator)
+            [this,
+             key = key,
+             validator = validator,
+             peers = std::move(peers),
+             type]() mutable {
                 updateSlotAndSquelch(key, validator, std::move(peers), type);
             });
 
@@ -1444,9 +1449,12 @@ OverlayImpl::updateSlotAndSquelch(
         return;
 
     if (!strand_.running_in_this_thread())
-        return post(strand_, [this, key, validator, peer, type]() {
-            updateSlotAndSquelch(key, validator, peer, type);
-        });
+        return post(
+            strand_,
+            // Must capture copies of reference parameters (i.e. key, validator)
+            [this, key = key, validator = validator, peer, type]() {
+                updateSlotAndSquelch(key, validator, peer, type);
+            });
 
     slots_.updateSlotAndSquelch(key, validator, peer, type, [&]() {
         reportInboundTraffic(TrafficCount::squelch_ignored, 0);
```
