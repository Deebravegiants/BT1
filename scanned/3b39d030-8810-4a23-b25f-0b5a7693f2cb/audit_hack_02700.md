# [M] The owner of the `VaultAdmin` contract can grief with high performance and withdrawal fees

## Summary
Severity: Medium
Reporter: berndartmueller
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L155-L170
Type: audit-issue

## Details
# The owner of the `VaultAdmin` contract can grief with high performance and withdrawal fees

## Summary

Withdrawal and performance fees can be set unreasonably high (almost 100%), causing huge losses for users.

## Vulnerability Detail

The owner of the `VaultAdmin` contract can change the performance fee and the withdrawal fee at any time up to a value of `ONE_64x64` (excluding `ONE_64x64`, `ONE_64x64` equals 100%).

Theoretically, it's possible to set the withdrawal fee close to a value of `ONE_64x64`, which would result in an (almost) complete loss of the user when withdrawing.

The same applies to the performance fee. The performance fee is collected whenever a new epoch is initialized. A performance fee close to 100% would collect almost all of the realized net income of an epoch.

It's advised to add reasonable upper bounds for fees, to prevent any trust issues.

## Impact

Withdrawals could result in an almost complete loss in the user's funds and an unreasonable high performance fee could take away almost all of the realized net income of an epoch.

## Code Snippet

[vault/VaultAdmin.setPerformanceFee64x64](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L155-L170)

```solidity
function setPerformanceFee64x64(int128 newPerformanceFee64x64)
    external
    onlyOwner
{
    VaultStorage.Layout storage l = VaultStorage.layout();
    require(newPerformanceFee64x64 < ONE_64x64, "fee > 1");

    emit PerformanceFeeSet(
        l.epoch,
        l.performanceFee64x64,
        newPerformanceFee64x64,
        msg.sender
    );

    l.performanceFee64x64 = newPerformanceFee64x64; // @audit-info Reasonable upper bound is missing here
}
```

[vault/VaultAdmin.setWithdrawalFee64x64](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L175-L190)

```solidity
function setWithdrawalFee64x64(int128 newWithdrawalFee64x64)
    external
    onlyOwner
{
    VaultStorage.Layout storage l = VaultStorage.layout();
    require(newWithdrawalFee64x64 < ONE_64x64, "fee > 1");

    emit WithdrawalFeeSet(
        l.epoch,
        l.withdrawalFee64x64,
        newWithdrawalFee64x64,
        msg.sender
    );

    l.withdrawalFee64x64 = newWithdrawalFee64x64; // @audit-info Reasonable upper bound is missing here
}
```

## Tool Used

Manual review

## Recommendation

Consider adding a reasonable upper bound for both `performanceFee64x64` and `withdrawalFee64x64`.
