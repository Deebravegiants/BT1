# [?] peer: fix nil deref in newPingPayload on BestBlockHeader error

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2026-03-24
Source: https://github.com/lightningnetwork/lnd/commit/9a2c4c67c4ccdf3ec2c254302ae2517a96064032
Type: security-commit

## Details
peer: fix nil deref in newPingPayload on BestBlockHeader error

The condition guarding the early return used && when it should have
used ||. When BestBlockHeader returns an error with a nil header, the
old code only short-circuited if the nil header equalled
lastBlockHeader. Otherwise it fell through to header.Serialize(),
causing a nil pointer dereference panic.

Change the condition to return the cached serialized header whenever
there is an error OR when the header is unchanged.
