# [?] Merge bitcoin/bitcoin#30394: net: fix race condition in self-connect detection

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2024-07-16
Source: https://github.com/ElementsProject/elements/commit/8db506f4063294f91cad2645499379054876bd11
Type: security-commit

## Details
Merge bitcoin/bitcoin#30394: net: fix race condition in self-connect detection

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

## Patch
### src/net.h
```diff
@@ -727,7 +727,7 @@ class NetEventsInterface
 {
 public:
     /** Initialize a peer (setup state, queue any initial messages) */
-    virtual void InitializeNode(CNode* pnode) = 0;
+    virtual void InitializeNode(const CNode* pnode) = 0;
 
     /** Handle removal of a peer (clear state) */
     virtual void FinalizeNode(const CNode& node) = 0;
```

### src/net_processing.cpp
```diff
@@ -222,6 +222,10 @@ struct Peer {
      * Most peers use headers-first syncing, which doesn't use this mechanism */
     uint256 m_continuation_block GUARDED_BY(m_block_inv_mutex) {};
 
+    Mutex m_msgproc_mutex;
+    /** Set to true once initial VERSION message was sent (only relevant for outbound peers). */
+    bool m_outbound_version_message_sent GUARDED_BY(m_msgproc_mutex){false};
+
     /** This peer's reported block height when we connected */
     std::atomic<int> m_starting_height{-1};
 
@@ -312,7 +316,7 @@ class PeerManagerImpl final : public PeerManager
     void NewPoWValidBlock(const CBlockIndex *pindex, const std::shared_ptr<const CBlock>& pblock) override;
 
     /** Implement NetEventsInterface */
-    void InitializeNode(CNode* pnode) override;
+    void InitializeNode(const CNode* pnode) override;
     void FinalizeNode(const CNode& node) override;
     bool ProcessMessages(CNode* pfrom, std::atomic<bool>& interrupt) override;
     bool SendMessages(CNode* pto) override EXCLUSIVE_LOCKS_REQUIRED(pto->cs_sendProcessing);
@@ -1189,7 +1193,7 @@ void UpdateLastBlockAnnounceTime(NodeId node, int64_t time_in_seconds)
     if (state) state->m_last_block_announcement = time_in_seconds;
 }
 
-void PeerManagerImpl::InitializeNode(CNode *pnode)
+void PeerManagerImpl::InitializeNode(const CNode *pnode)
 {
     NodeId nodeid = pnode->GetId();
     {
@@ -1202,9 +1206,6 @@ void PeerManagerImpl::InitializeNode(CNode *pnode)
         LOCK(m_peer_mutex);
         m_peer_map.emplace_hint(m_peer_map.end(), nodeid, std::move(peer));
     }
-    if (!pnode->IsInboundConn()) {
-        PushNodeVersion(*pnode);
-    }
 }
 
 void PeerManagerImpl::ReattemptInitialBroadcast(CScheduler& scheduler)
@@ -4201,6 +4202,10 @@ bool PeerManagerImpl::ProcessMessages(CNode* pfrom, std::atomic<bool>& interrupt
     PeerRef peer = GetPeerRef(pfrom->GetId());
     if (peer == nullptr) return false;
 
+    // For outbound connections, ensure that the initial VERSION message
+    // has been sent first before processing any incoming messages
+    if (!pfrom->IsInboundConn() && WITH_LOCK(peer->m_msgproc_mutex, return !peer->m_outbound_version_message_sent)) return false;
+
     {
         LOCK(peer->m_getdata_requests_mutex);
         if (!peer->m_getdata_requests.empty()) {
@@ -4660,6 +4665,13 @@ bool PeerManagerImpl::SendMessages(CNode* pto)
     // disconnect misbehaving peers even before the version handshake is complete.
     if (MaybeDiscourageAndDisconnect(*pto, *peer)) return true;
 
+    // Initiate version handshake for outbound connections
+    if (!pto->IsInboundConn() && WITH_LOCK(peer->m_msgproc_mutex, return !peer->m_outbound_version_message_sent)) {
+        LOCK(peer->m_msgproc_mutex);
+        PushNodeVersion(*pto);
+        peer->m_outbound_version_message_sent = true;
+    }
+
     // Don't send anything until the version handshake is complete
     if (!pto->fSuccessfullyConnected || pto->fDisconnect)
         return true;
```

### src/test/fuzz/util.cpp
```diff
@@ -244,13 +244,13 @@ void FillNode(FuzzedDataProvider& fuzzed_data_provider, ConnmanTestMsg& connman,
                 filter_txs),
     };
 
-    (void)connman.ReceiveMsgFrom(node, msg_version);
-    node.fPauseSend = false;
-    connman.ProcessMessagesOnce(node);
     {
         LOCK(node.cs_sendProcessing);
         peerman.SendMessages(&node);
     }
+    (void)connman.ReceiveMsgFrom(node, msg_version);
+    node.fPauseSend = false;
+    connman.ProcessMessagesOnce(node);
     if (node.fDisconnect) return;
     assert(node.nVersion == version);
     assert(node.GetCommonVersion() == std::min(version, PROTOCOL_VERSION));
```
