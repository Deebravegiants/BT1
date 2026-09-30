# [M] VaultTracker has the wrong admin

## Summary
Severity: Medium
Contest weight: 0.1032
Dataset id: 15813
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`MarketPlace.createMarket()` calls `Creator.create()` which creates an instance of `ZcToken` and a `VaultTracker`. `VaultTracker` takes `msg.sender` as the admin. We know that if contract A calls contract B which calls contract C, `msg.sender` in contract C is the address of B i.e. the `msg.sender` in VaultTracker is the address of the creator contract. However, the creator contract is not able (and not supposed to) interact with the VaultTracker unlike the marketplace contract.

## Recommendation
Modify the constructor of the VaultTracker contract so that the creator contract can pass in msg.sender (MarketPlace’s address) to be used as admin.

Using this as the main `admin` constructor issue. Given it is admin related, I believe going with the Medium issue instead of #134 makes sense.

**[robrobbins (Swivel) resolved](https://github.com/code-423n4/2022-07-swivel-findings/issues/36#issuecomment-1209654129):**

See [#134](https://github.com/code-423n4/2022-07-swivel-findings/issues/134).
