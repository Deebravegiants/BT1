# [?] Fix unsoundness in RawVal::get_tag (#773)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/rs-soroban-env
Published: 2023-04-29
Source: https://github.com/stellar/rs-soroban-env/commit/e5cdfd871093e002428f924162152df248a0e22b
Type: security-commit

## Details
Fix unsoundness in RawVal::get_tag (#773)

* Remove gaps from Tag discriminants

* Update test wasms

Built with sdk commit 9383a6ae6f21c24cfe74a53759949b2c83d53e78

* Extract Tag::from_u8 from RawVal::get_tag

* Add test for Tag::from_u8

---------

Co-authored-by: Graydon Hoare <graydon@pobox.com>
