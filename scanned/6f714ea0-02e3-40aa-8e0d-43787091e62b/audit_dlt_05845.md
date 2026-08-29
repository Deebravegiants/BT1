# [?] Harden tonlib against crashes (#2406)

## Summary
Severity: Unknown
Chain: TON
Component: ton-blockchain/ton
Published: 2026-06-15
Source: https://github.com/ton-blockchain/ton/commit/4c92183c86f51768ca74dff02c78fae7b057f31a
Type: security-commit

## Details
Harden tonlib against crashes (#2406)

* Harden tonlib against malformed inputs

* Handle VM exceptions in SmartContract runner

* Validate tonlib log message verbosity

* Limit tonlib missing library fetches

* Harden smc-envelope message builders

* Catch exceptions at tonlib JSON boundaries

* Limit tonlib TVM stack output depth

* Retry external message packing with referenced body

* Format tonlib hardening changes

* Harden tonlib transaction list handling

* Reject invalid tonlib external messages

* Handle tonlib BOC serialization errors

* Catch tonlib proof processing exceptions

* Harden tonlib shard info proof parsing

* Formatting

---------

Co-authored-by: SpyCheese <mikle98@yandex.ru>
