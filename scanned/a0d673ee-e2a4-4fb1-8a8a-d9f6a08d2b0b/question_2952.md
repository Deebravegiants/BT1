# Q2952: convert_permissioned_burn_config settles one authorization twice (parse_token_extension.rs)

## Question
Can an unprivileged attacker entering through one JSON-RPC call or websocket subscription from a single client, at most once per CLUSTER_SLOT_TIME_TARGET/2 reach `convert_permissioned_burn_config` in `account-decoder/src/parse_token_extension.rs` with a payload that satisfies the cheap precondition but not the full check, and have `convert_permissioned_burn_config` apply the same authorized effect a second time, so that the invariant "One signed authorization produces exactly one state effect." breaks and the result is Loss of Funds?

## Target
- File/function: `account-decoder/src/parse_token_extension.rs` -> `convert_permissioned_burn_config()` (around line 447)
- Entrypoint: one JSON-RPC call or websocket subscription from a single client, at most once per CLUSTER_SLOT_TIME_TARGET/2
- Attacker controls: a payload that satisfies the cheap precondition but not the full check
- Exploit idea: Get `convert_permissioned_burn_config` to apply the same logical effect twice from a single user authorization by re-entering it or replaying the surrounding flow.
- Invariant to test: One signed authorization produces exactly one state effect.
- Expected Immunefi impact: Loss of Funds - theft or creation of lamports/tokens without the owner's signature (6,250-25,000 SOL)
- Fast validation: Integration test: submit the flow twice (and once re-entrantly) and assert the second application is rejected and balances moved once.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can replay or double-apply one signed transaction through durable-nonce advance, blockhash-queue aging, or status-cache dedup so a single authorization settles more than once.
