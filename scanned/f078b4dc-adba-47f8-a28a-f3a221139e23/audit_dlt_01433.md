# [?] Merge bitcoin/bitcoin#34060: test: fix race condition in p2p_v2_misbehaving.py peerid assertion

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2025-12-16
Source: https://github.com/bitcoin/bitcoin/commit/cbafd3ddf8a27ee1aa22feb5aecde86498e44a1d
Type: security-commit

## Details
Merge bitcoin/bitcoin#34060: test: fix race condition in p2p_v2_misbehaving.py peerid assertion

09dfa4d3f8dfbea61a73d4add79e2464ca776571 test: fix race condition in p2p_v2_misbehaving.py peerid assertion (stratospher)

Pull request description:

  Remove the hard-coded peer id from the debug message in `p2p_v2_misbehaving.py`.

  asyncio's non-deterministic task scheduling might cause [peer2](https://github.com/bitcoin/bitcoin/blob/938d7aacabd0bb3784bb3e529b1ed06bb2891864/test/functional/p2p_v2_misbehaving.py#L181)'s connection to happen before [peer1](https://github.com/bitcoin/bitcoin/blob/938d7aacabd0bb3784bb3e529b1ed06bb2891864/test/functional/p2p_v2_misbehaving.py#L179)'s. since we test that peer2 [remains connected](https://github.com/bitcoin/bitcoin/blob/938d7aacabd0bb3784bb3e529b1ed06bb2891864/test/functional/p2p_v2_misbehaving.py#L182), any disconnection must originate from peer1, making the specific peer id not necessary for test correctness. so we can remove the hard coded peer id from the expected debug log message.

  Fixes #34035.

ACKs for top commit:
  maflcko:
    lgtm ACK 09dfa4d3f8dfbea61a73d4add79e2464ca776571
  mzumsande:
    Code Review ACK 09dfa4d3f8dfbea61a73d4add79e2464ca776571

Tree-SHA512: 542b08ddae09db7454e8c08b1d26aade50a53c2505683df99556cf071a6a38195b64f8700f6db3f4e1b318497fc4b5232246ad4e9d6f3af45fad83e333fa91fb
