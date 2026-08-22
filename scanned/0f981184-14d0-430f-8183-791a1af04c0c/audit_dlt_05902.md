# [?] [fix] #3928: Fix double free in wasm tests

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger/iroha
Published: 2023-09-28
Source: https://github.com/hyperledger-iroha/iroha/commit/f6f4a9fdc5a66781027374aa1ad7b7d7667644c6
Type: security-commit

## Details
[fix] #3928: Fix double free in wasm tests

The `log` and `dbg` functions do not take the pointer ownership, but their mock versions used for testing did

Signed-off-by: Nikita Strygin <dcnick3@users.noreply.github.com>
