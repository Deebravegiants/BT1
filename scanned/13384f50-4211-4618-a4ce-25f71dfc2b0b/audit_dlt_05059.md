# [H] Remote memory exhaustion attack on ckb nodes

## Summary
Severity: High
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-07-26
Source: https://github.com/nervosnetwork/ckb/security/advisories/GHSA-48vq-8jqv-gm6f
Type: github-advisory

## Details
In the ckb sync protocol, SyncState maintains a HashMap called 'misbehavior' that keeps a score of a peer's violations of the protocol. This HashMap is keyed to PeerIndex (an alias for SessionId), and entries are never removed from it. SessionId is an integer that increases monotonically with every new connection.

A remote attacker can manipulate this HashMap to grow forever, resulting in degraded performance and ultimately a panic on allocation failure or being killed by the OS, depending on the platform.

This is a critical severity security bug. It could be exploited to create a targeted or network-wide denial of service, to reduce the hash power of the network as part of a 51% attack, and perhaps in other creative ways.

An attack is trivial:

1. connect to another node
2. send an invalid sync protocol request, such as `SendHeaders` for non-consecutive blocks
3. disconnect
4. repeat
