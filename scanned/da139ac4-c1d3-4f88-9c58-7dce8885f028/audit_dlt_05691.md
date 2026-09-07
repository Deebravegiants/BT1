# [?] p2p/nodestate: fix deadlock during shutdown of les server (#21927)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-11-30
Source: https://github.com/celo-org/celo-blockchain/commit/e7db1dbc96fb366c13e05ee9b3b0a57ba26ca49b
Type: security-commit

## Details
p2p/nodestate: fix deadlock during shutdown of les server (#21927)

This PR fixes a deadlock reported here: #21925

The cause is that many operations may be pending, but if the close happens, only one of them gets awoken and exits, the others remain waiting for a signal that never comes.
