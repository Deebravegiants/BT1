# [?] Fix crash inside `OverlayImpl` loops over `ids_` (#5071)

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2024-08-02
Source: https://github.com/XRPLF/rippled/commit/ffc343a2bc274ee81db9a3cef050e4fd674507a6
Type: security-commit

## Details
Fix crash inside `OverlayImpl` loops over `ids_` (#5071)

## Patch
### src/test/overlay/tx_reduce_relay_test.cpp
```diff
@@ -189,7 +189,10 @@ class tx_reduce_relay_test : public beast::unit_test::suite
             consumer,
             std::move(stream_ptr),
             overlay);
+        BEAST_EXPECT(
+            overlay.findPeerByPublicKey(key) == std::shared_ptr<PeerImp>{});
         overlay.add_active(peer);
+        BEAST_EXPECT(overlay.findPeerByPublicKey(key) == peer);
         peers.emplace_back(peer);  // overlay stores week ptr to PeerImp
         lid_ += 2;
         rid_ += 2;
```

### src/xrpld/overlay/detail/OverlayImpl.cpp
```diff
@@ -1163,9 +1163,11 @@ OverlayImpl::getActivePeers(
     disabled = enabledInSkip = 0;
     ret.reserve(ids_.size());
 
+    // NOTE The purpose of p is to delay the destruction of PeerImp
+    std::shared_ptr<PeerImp> p;
     for (auto& [id, w] : ids_)
     {
-        if (auto p = w.lock())
+        if (p = w.lock(); p != nullptr)
         {
             bool const reduceRelayEnabled = p->txReduceRelayEnabled();
             // tx reduced relay feature disabled
@@ -1205,9 +1207,11 @@ std::shared_ptr<Peer>
 OverlayImpl::findPeerByPublicKey(PublicKey const& pubKey)
 {
     std::lock_guard lock(mutex_);
+    // NOTE The purpose of peer is to delay the destruction of PeerImp
+    std::shared_ptr<PeerImp> peer;
     for (auto const& e : ids_)
     {
-        if (auto peer = e.second.lock())
+        if (peer = e.second.lock(); peer != nullptr)
         {
             if (peer->getNodePublic() == pubKey)
                 return peer;
```
