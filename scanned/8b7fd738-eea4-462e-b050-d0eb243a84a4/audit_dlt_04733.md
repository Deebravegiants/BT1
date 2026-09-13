# [M] Withdrawal fee receiver can DoS withdrawals

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/133
Type: sherlock-finding

## Details
berndartmueller

medium

# Withdrawal fee receiver can DoS withdrawals

## Summary

The withdrawal fee receiver can DoS withdrawals by reverting the `POOL` token transfer within the `onERC1155Received` transfer hook.

## Vulnerability Detail

Withdrawal fees are transferred to the fee `receiver` in the `VaultInternal._withdraw` function. Internally, this function calls the `VaultInternal._collectWithdrawalFee` function. Then within this function, the `VaultInternal._transferCollateralAndShortAssets` function is called.

Fees are then transferred by using `Pool.safeTransferFrom`. `POOL` itself is an `ERC1155` token, hence, due to using the `safeTransferFrom` function, the `onERC1155Received` hook is called on the `receiver`. If the `receiver` is a smart contract, it is therefore possible to revert the transfer and prevent withdrawals.

## Impact

The withdrawal fee receiver can prevent withdrawals.

## Code Snippet

[vault/VaultInternal.\_withdraw](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L277)

```solidity
function _withdraw(
    address caller,
    address receiver,
    address owner,
    uint256 assetAmount,
    uint256 shareAmount
) private {
    [..]

    // calculate the collateral amount and short contract amount distribution
    (uint256 collateralAmount, uint256 shortContracts) =
        _calculateDistributions(l, assetAmount);

    // calculates and deducts the withdrawal fee
    (uint256 collateralAmountSansFee, uint256 shortContractsSansFee) =
        _collectWithdrawalFee(l, collateralAmount, shortContracts);

    // transfers the collateral and short contracts to the receiver
    _transferCollateralAndShortAssets(
        _lastEpoch(l),
        collateralAmountSansFee,
        shortContractsSansFee,
        _lastOption(l).shortTokenId,
        receiver
    );

    emit Withdraw(caller, receiver, owner, assetAmount, shareAmount);
}
```

[vault/VaultInternal.\_collectWithdrawalFee](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L383-L389)

```solidity
function _collectWithdrawalFee(
    VaultStorage.Layout storage l,
    uint256 collateralAmount,
    uint256 shortContracts
) private returns (uint256, uint256) {
    // calculates the collateral fee
    uint256 feeInCollateral = l.withdrawalFee64x64.mulu(collateralAmount);

    // calculates the short contract fee
    uint256 feesInShortContracts =
        l.withdrawalFee64x64.mulu(shortContracts);

    VaultStorage.Option memory lastOption = _lastOption(l);
    uint64 epoch = _lastEpoch(l);

    // transfers the fees to the fee recipient
    _transferCollateralAndShortAssets(
        epoch,
        feeInCollateral,
        feesInShortContracts,
        lastOption.shortTokenId,
        l.feeRecipient
    );

    emit WithdrawalFeeCollected(
        epoch,
        feeInCollateral,
        feesInShortContracts
    );

    // deducts the fee from collateral and short contract amounts
    return (
        collateralAmount - feeInCollateral,
        shortContracts - feesInShortContracts
    );
}
```

[vault/VaultInternal.\_transferCollateralAndShortAssets](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L426-L432)

```solidity
function _transferCollateralAndShortAssets(
    uint64 epoch,
    uint256 collateralAmount,
    uint256 shortContracts,
    uint256 shortTokenId,
    address receiver
) private {
    if (collateralAmount > 0) {
        // transfers collateral to receiver
        ERC20.safeTransfer(receiver, collateralAmount);
    }

    if (shortContracts > 0) {
        // transfers short contracts to receiver
        Pool.safeTransferFrom(
            address(this),
            receiver,
            shortTokenId,
            shortContracts,
            ""
        );
    }

    emit DistributionSent(
        epoch,
        collateralAmount,
        shortContracts,
        receiver
    );
}
```

## Tool Used

Manual review

## Recommendation

Consider using a pull-based approach for withdrawal fees instead of immediately transferring the fees to the recipient. This would allow the withdrawal fee receiver to withdraw the fees at any time, but would not allow them to block withdrawals.
