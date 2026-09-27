# [?] Merge bitcoin/bitcoin#30394: net: fix race condition in self-connect detection

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2024-07-16
Source: https://github.com/ElementsProject/elements/commit/c577f5afb44e7d204d6d68e2c73e95f12138c1bd
Type: security-commit

## Details
Merge bitcoin/bitcoin#30394: net: fix race condition in self-connect detection

ELEMENTS: cherry-picked before ElementsProject/elements#1472 for ease of
merge

16bd283b3ad05daa41259a062aee0fc05b463fa6 Reapply "test: p2p: check that connecting to ourself leads to disconnect" (Sebastian Falbesoner)
0dbcd4c14855fe2cba15a32245572b693dc18c4e net: prevent sending messages in `NetEventsInterface::InitializeNode` (Sebastian Falbesoner)
66673f1c1302c986e344c7f44bb0b352213d5dc8 net: fix race condition in self-connect detection (Sebastian Falbesoner)

Pull request description:

  This PR fixes a recently discovered race condition in the self-connect detection (see #30362 and #30368).

  Initiating an outbound network connection currently involves the following steps after the socket connection is established (see [`CConnman::OpenNetworkConnection`](https://github.com/bitcoin/bitcoin/blob/bd5d1688b4311e21c0e0ff89a3ae02ef7d0543b8/src/net.cpp#L2923-L2930) method):
  1. set up node state
  2. queue VERSION message (both steps 1 and 2 happen in [`InitializeNode`](https://github.com/bitcoin/bitcoin/blob/bd5d1688b4311e21c0e0ff89a3ae02ef7d0543b8/src/net_processing.cpp#L1662-L1683))
  3. add new node to vector `m_nodes`

  If we connect to ourself, it can happen that the sent VERSION message (step 2) is received and processed locally *before* the node object is added to the connection manager's `m_nodes` vector (step 3). In this case, the self-connect remains undiscovered, as the detection doesn't find the outbound peer in `m_nodes` yet (see `CConnman::CheckIncomingNonce`).

  Fix this by swapping the order of 2. and 3., by taking the `PushNodeVersion` call out of `InitializeNode` and doing that in the `SendMessages` method instead, which is only called for `CNode` instances in `m_nodes`.

  The temporarily reverted test introduced in #30362 is readded. Fixes #30368.

  Thanks go to vasild, mzumsande and dergoegge for suggestions on how to fix this (see https://github.com/bitcoin/bitcoin/issues/30368#issuecomment-2200625017 ff. and https://github.com/bitcoin/bitcoin/pull/30394#discussion_r1668290789).

ACKs for top commit:
  naiyoma:
    tested ACK [https://github.com/bitcoin/bitcoin/pull/30394/commits/16bd283b3ad05daa41259a062aee0fc05b463fa6](https://github.com/bitcoin/bitcoin/pull/30394/commits/16bd283b3ad05daa41259a062aee0fc05b463fa6),  built and tested locally,  test passes successfully.
  mzumsande:
    ACK 16bd283b3ad05daa41259a062aee0fc05b463fa6
  tdb3:
    ACK 16bd283b3ad05daa41259a062aee0fc05b463fa6
  glozow:
    ACK 16bd283b3ad05daa41259a062aee0fc05b463fa6
  dergoegge:
    ACK 16bd283b3ad05daa41259a062aee0fc05b463fa6

Tree-SHA512: 5b8aced6cda8deb38d4cd3fe4980b8af505d37ffa0925afaa734c5d81efe9d490dc48a42e1d0d45dd2961c0e1172a3d5b6582ae9a2d642f2592a17fbdc184445
(cherry picked from commit 35dddbccf1fba3239b836c210c6a5eca88bf2311)

### src/net.h
```diff
@@ -752,8 +752,8 @@ class NetEventsInterface
     /** Mutex for anything that is only accessed via the msg processing thread */
     static Mutex g_msgproc_mutex;
 
-    /** Initialize a peer (setup state, queue any initial messages) */
-    virtual void InitializeNode(CNode& node, ServiceFlags our_services) = 0;
+    /** Initialize a peer (setup state) */
+    virtual void InitializeNode(const CNode& node, ServiceFlags our_services) = 0;
 
     /** Handle removal of a peer (clear state) */
     virtual void FinalizeNode(const CNode& node) = 0;
```

### src/net_processing.cpp
```diff
@@ -241,6 +241,9 @@ struct Peer {
      * Most peers use headers-first syncing, which doesn't use this mechanism */
     uint256 m_continuation_block GUARDED_BY(m_block_inv_mutex) {};
 
+    /** Set to true once initial VERSION message was sent (only relevant for outbound peers). */
+    bool m_outbound_version_message_sent GUARDED_BY(NetEventsInterface::g_msgproc_mutex){false};
+
     /** This peer's reported block height when we connected */
     std::atomic<int> m_starting_height{-1};
 
@@ -495,7 +498,7 @@ class PeerManagerImpl final : public PeerManager
         EXCLUSIVE_LOCKS_REQUIRED(!m_most_recent_block_mutex);
 
     /** Implement NetEventsInterface */
-    void InitializeNode(CNode& node, ServiceFlags our_services) override EXCLUSIVE_LOCKS_REQUIRED(!m_peer_mutex);
+    void InitializeNode(const CNode& node, ServiceFlags our_services) override EXCLUSIVE_LOCKS_REQUIRED(!m_peer_mutex);
     void FinalizeNode(const CNode& node) override EXCLUSIVE_LOCKS_REQUIRED(!m_peer_mutex, !m_headers_presync_mutex);
     bool ProcessMessages(CNode* pfrom, std::atomic<bool>& interrupt) override
         EXCLUSIVE_LOCKS_REQUIRED(!m_peer_mutex, !m_recent_confirmed_transactions_mutex, !m_most_recent_block_mutex, !m_headers_presync_mutex, g_msgproc_mutex);
@@ -1464,7 +1467,7 @@ void PeerManagerImpl::UpdateLastBlockAnnounceTime(NodeId node, int64_t time_in_s
     if (state) state->m_last_block_announcement = time_in_seconds;
 }
 
-void PeerManagerImpl::InitializeNode(CNode& node, ServiceFlags our_services)
+void PeerManagerImpl::InitializeNode(const CNode& node, ServiceFlags our_services)
 {
     NodeId nodeid = node.GetId();
     {
@@ -1477,9 +1480,6 @@ void PeerManagerImpl::InitializeNode(CNode& node, ServiceFlags our_services)
         LOCK(m_peer_mutex);
         m_peer_map.emplace_hint(m_peer_map.end(), nodeid, peer);
     }
-    if (!node.IsInboundConn()) {
-        PushNodeVersion(node, *peer);
-    }
 }
 
 void PeerManagerImpl::ReattemptInitialBroadcast(CScheduler& scheduler)
@@ -4999,6 +4999,10 @@ bool PeerManagerImpl::ProcessMessages(CNode* pfrom, std::atomic<bool>& interrupt
     PeerRef peer = GetPeerRef(pfrom->GetId());
     if (peer == nullptr) return false;
 
+    // For outbound connections, ensure that the initial VERSION message
+    // has been sent first before processing any incoming messages
+    if (!pfrom->IsInboundConn() && !peer->m_outbound_version_message_sent) return false;
+
     {
         LOCK(peer->m_getdata_requests_mutex);
         if (!peer->m_getdata_requests.empty()) {
@@ -5497,6 +5501,12 @@ bool PeerManagerImpl::SendMessages(CNode* pto)
     // disconnect misbehaving peers even before the version handshake is complete.
     if (MaybeDiscourageAndDisconnect(*pto, *peer)) return true;
 
+    // Initiate version handshake for outbound connections
+    if (!pto->IsInboundConn() && !peer->m_outbound_version_message_sent) {
+        PushNodeVersion(*pto, *peer);
+        peer->m_outbound_version_message_sent = true;
+    }
+
     // Don't send anything until the version handshake is complete
     if (!pto->fSuccessfullyConnected || pto->fDisconnect)
         return true;
```

### src/test/util/net.cpp
```diff
@@ -25,7 +25,8 @@ void ConnmanTestMsg::Handshake(CNode& node,
     const CNetMsgMaker mm{0};
 
     peerman.InitializeNode(node, local_services);
-    FlushSendBuffer(node); // Drop the version message added by InitializeNode.
+    peerman.SendMessages(&node);
+    FlushSendBuffer(node); // Drop the version message added by SendMessages.
 
     CSerializedNetMsg msg_version{
         mm.Make(NetMsgType::VERSION,
```
