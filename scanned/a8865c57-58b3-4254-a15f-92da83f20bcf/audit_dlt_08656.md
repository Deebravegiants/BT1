# [?] fixed crash in adnl

## Summary
Severity: Unknown
Chain: TON
Component: ton-blockchain/ton
Published: 2020-02-29
Source: https://github.com/ton-blockchain/ton/commit/27aaa1152407f8b119f383e5e57fe7847354adae
Type: security-commit

## Details
fixed crash in adnl

## Patch
### adnl/adnl-peer.cpp
```diff
@@ -147,7 +147,7 @@ void AdnlPeerPairImpl::receive_packet_checked(AdnlPacket packet) {
     return;
   }
   if (packet.seqno() > 0) {
-    if (received_packet(static_cast<td::uint32>(packet.seqno()))) {
+    if (received_packet(packet.seqno())) {
       VLOG(ADNL_INFO) << this << ": dropping IN message: old seqno: " << packet.seqno() << " (current max " << in_seqno_
                       << ")";
       return;
@@ -165,7 +165,7 @@ void AdnlPeerPairImpl::receive_packet_checked(AdnlPacket packet) {
   // delivering
 
   if (packet.seqno() > 0) {
-    add_received_packet(static_cast<td::uint32>(packet.seqno()));
+    add_received_packet(packet.seqno());
   }
 
   if (packet.confirm_seqno() > ack_seqno_) {
```

### adnl/adnl-peer.hpp
```diff
@@ -123,7 +123,7 @@ class AdnlPeerPairImpl : public AdnlPeerPair {
   td::Result<td::actor::ActorId<AdnlNetworkConnection>> get_conn();
   void create_channel(pubkeys::Ed25519 pub, td::uint32 date);
 
-  bool received_packet(td::uint32 seqno) const {
+  bool received_packet(td::uint64 seqno) const {
     CHECK(seqno > 0);
     if (seqno + 64 <= in_seqno_) {
       return true;
@@ -134,7 +134,7 @@ class AdnlPeerPairImpl : public AdnlPeerPair {
     return recv_seqno_mask_ & (1ull << (in_seqno_ - seqno));
   }
 
-  void add_received_packet(td::uint32 seqno) {
+  void add_received_packet(td::uint64 seqno) {
     CHECK(!received_packet(seqno));
     if (seqno <= in_seqno_) {
       recv_seqno_mask_ |= (1ull << (in_seqno_ - seqno));
```
