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


_Trimmed to 38 lines — full report: https://github.com/ElementsProject/elements/commit/c577f5afb44e7d204d6d68e2c73e95f12138c1bd_
