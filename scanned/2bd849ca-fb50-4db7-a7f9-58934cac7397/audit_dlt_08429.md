# [?] document DOS exposure and mitigation

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2018-05-23
Source: https://github.com/cometbft/cometbft/commit/e0d4fe2dba27b517d9875224c227b0ac09f3323c
Type: security-commit

## Details
document DOS exposure and mitigation

Refs #1494

## Patch
### docs/running-in-production.rst
```diff
@@ -48,3 +48,87 @@ precommit from the WAL.
 
 Make sure to read about `WAL corruption
 <./specification/corruption.html#wal-corruption>__` and recovery strategies.
+
+DOS Exposure and Mitigation
+---------------------------
+
+Validators are supposed to setup `Sentry Node Architecture
+<https://blog.cosmos.network/tendermint-explained-bringing-bft-based-pos-to-the-public-blockchain-domain-f22e274a0fdb>__`
+to prevent Denial-of-service attacks. You can read more about it `here
+<https://github.com/tendermint/aib-data/blob/develop/medium/TendermintBFT.md>__`.
+
+Blockchain Reactor
+~~~~~~~~~~~~~~~~~~
+
+Defines ``maxMsgSize`` for the maximum size of incoming messages,
+``SendQueueCapacity`` and ``RecvBufferCapacity`` for maximum sending and
+receiving buffers respectively. These are supposed to prevent amplification
+attacks by setting up the upper limit on how much data we can receive & send to
+a peer.
+
+Sending incorrectly encoded data will result in stopping the peer.
+
+Consensus Reactor
+~~~~~~~~~~~~~~~~~
+
+Defines 4 channels: state, data, vote and vote_set_bits. Each channel
+has  ``SendQueueCapacity`` and ``RecvBufferCapacity`` and
+``RecvMessageCapacity`` set to ``maxMsgSize``.
+
+Sending incorrectly encoded data will result in stopping the peer.
+
+Evidence Reactor
+~~~~~~~~~~~~~~~~
+
+`#1503 <https://github.com/tendermint/tendermint/issues/1503>__`
+
+Sending invalid evidence will result in stopping the peer.
+
+Sending incorrectly encoded data or data exceeding ``maxMsgSize`` will result
+in stopping the peer.
+
+PEX Reactor
+~~~~~~~~~~~
+
+Defines only ``SendQueueCapacity``. `#1503 <https://github.com/tendermint/tendermint/issues/1503>__`
+
+Implements rate-limiting by enforcing minimal time between two consecutive
+``pexRequestMessage`` requests. If the peer sends us addresses we did not ask,
+it is stopped.
+
+Sending incorrectly encoded data or data exceeding ``maxMsgSize`` will result
+in stopping the peer.
+
+Mempool Reactor
+~~~~~~~~~~~~~~~
+
+`#1503 <https://github.com/tendermint/tendermint/issues/1503>__`
+
+Mempool maintains a cache of the last 10000 transactions to prevent replaying
+old transactions (plus transactions coming from other validators, who are
+continually exchanging transactions). Read `Replay Protection
+<./app-development.html#replay-protection>` for details.
+
+Sending incorrectly encoded data or data exceeding ``maxMsgSize`` will result
+in stopping the peer.
+
+P2P
+~~~
+
+The core of the Tendermint peer-to-peer system is ``MConnection``. Each
+connection has ``MaxPacketMsgPayloadSize``, which is the maximum packet size
+and bounded send & receive queues. One can impose restrictions on send &
+receive rate per connection (``SendRate``, ``RecvRate``).
+
+RPC
+~~~
+
+Endpoints returning multiple entries are limited by default to return 30
+elements (100 max).
+
+Rate-limiting and authentication are another key aspects to help protect
+against DOS attacks. While in the future we may implement these features, for
+now, validators are supposed to use external tools like `NGINX
+<https://www.nginx.com/blog/rate-limiting-nginx/>__` or `traefik
+<https://docs.traefik.io/configuration/commons/#rate-limiting>__` to archive
+the same things.
```
