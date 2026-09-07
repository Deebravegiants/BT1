# [?] C01: native ERC20 double spend (#779)

## Summary
Severity: Unknown
Chain: Uniswap
Component: Uniswap/v4-core
Published: 2024-07-14
Source: https://github.com/Uniswap/v4-core/commit/4287ddf9c35bf37c6a81e45cfe2fb9dcae00fa28
Type: security-commit

## Details
C01: native ERC20 double spend (#779)

* Add test verifying vulnerability

* c-01: enforcing strict sync, send, settle rules

* make sync external

* add comment explaining the NativeERC20 contract

* Moved AlreadySynced() error to Reserves

* Implemented comment feedback

* reverted renaming

* reverted renaming of constant

* renaming for clarity

* only reset currency after erc20 settle

* updated snaps

* correctly cast to address

* updated comment in settle function

* updated NativeERC20 test

* resolved feedback

* Updated getReserves in TransientStateLibrary

* fixed tests after renaming getReserves

* Rename reset to resetCurrency


_Trimmed to 38 lines — full report: https://github.com/Uniswap/v4-core/commit/4287ddf9c35bf37c6a81e45cfe2fb9dcae00fa28_
