# [M] CL-2021-04: Mplex unlimited open streams + decode problems, but saved by snappy-frame decoding edge-case

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: Teku
Published: 2021-12-01
Source: https://github.com/ConsenSys/teku/pull/3738
Type: ef-disclosure

## Details
Affected Clients: Teku
Uid: CL-2021-04
Bug: Mplex unlimited open streams + decode problems, but saved by snappy-frame decoding edge-case
Type: DoS
Summary: Teku does not spawn many threads, but does allocate more per basic stream. Due to a snappy-frame decoding bug (if mplex frame is smaller than snappy frame), the payload is silently ignored, and it does not hang on it. But remove the protocol negotiation, and just spawn 100.000 (or many more) open streams, by just sending the create frames. Unsure if it works better with a 1 byte title per frame. Adds min. 2-3 GB of memory to running node, and makes JVM heap go jump up and down multiple gigabytes repeatedly for minutes on end per attack (giving GC a hard time too).
Links: [https://github.com/ConsenSys/teku/pull/3738](https://github.com/ConsenSys/teku/pull/3738)
Reported: 2021-02-12
Fixed Date: 2021-03-18
Published: 2021-12-01
Severity: Medium
Bounty Hunter: Proto
