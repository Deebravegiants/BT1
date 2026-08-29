# [?] feat(ironfish): Fix double spend issue in transaction expiration (#3523)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2023-02-27
Source: https://github.com/iron-fish/ironfish/commit/23e45af925b75437be0050762f41a443fa6a46c9
Type: security-commit

## Details
feat(ironfish): Fix double spend issue in transaction expiration (#3523)

* feat(ironfish): Create `nullifierToTransactionHash` store

* feat(ironfish): Create `nullifierToTransactionHash` store (#3518)

* feat(ironfish): Update nullifier to transaction hash store

* feat(ironfish): Check nullifier -> transaction hash befor marking notes as unspent (#3520)

* feat(ironfish): Backfill `nullifierToTransactionHash` (#3522)

* feat(ironfish): Backfill `nullifierToTransactionHash`

* refactor(ironfish): Clean up output string

* refactor(ironfish): Update log from assets

* fix(ironfish): Only add unspent note hash if expiring the tx
