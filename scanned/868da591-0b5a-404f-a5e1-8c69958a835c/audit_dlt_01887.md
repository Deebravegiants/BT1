# [?] fix(node/sysgo-tests): attempt to fix race condition in p2p disconnect rpc call (op-rs/kona#2761)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2025-08-26
Source: https://github.com/ethereum-optimism/optimism/commit/a6c9d7a36c2b955b4bfa12ec426b559d5d406843
Type: security-commit

## Details
fix(node/sysgo-tests): attempt to fix race condition in p2p disconnect rpc call (op-rs/kona#2761)

## Description

It seems the `opp2p_disconnect` rpc call returns too early. This method
ensures that we're checking the peers are effectively not connected to
each other in the `opp2p_peers` call.
