# [C] Caller Validation in FXPool::onJoinPool()/onExitPool()

## Summary
Severity: Critical
Contest weight: 0.6358
Dataset id: 13437
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Xave, the key FXPool stablecoin pool is built on top of the BalancerV2 Vault. It is essentially composed of three main hooks that the BalancerV2 calls: onJoinPool() (upon liquidity provider deposit), onExitPool() (upon liquidity provider withdrawal), and onSwap() (upon user trade). Our analysis shows that two of them need to be revised to apply caller validation to ensure they can only be involved from the BalancerV2 Vault.

To elaborate, we show below the implementation of this onJoinPool() routine. As mentioned earlier, it is invoked when joining the pool. As a result, there is a need to ensure that it can only be called from the vault. Our analysis shows that the caller validation is not performed in the current implementation. The same is also applicable to the onExitPool() logic. Note that the onSwap() function has the proper caller validation in place.

```solidity
function onJoinPool(
    bytes32 poolId,
    address, // sender
    address recipient,
    uint256[] memory currentBalances, // @todo for vault transfers
    uint256,
    uint256,
    bytes calldata userData
) external override whenNotPaused returns (uint256[] memory amountsIn, uint256[] memory dueProtocolFeeAmounts) {
    (uint256 totalDepositNumeraire, address[] memory assetAddresses) = abi.decode(
        userData,
        (uint256, address[])
    );
    _enforceCap(totalDepositNumeraire);
    (uint256 lpTokens, uint256[] memory amountToDeposit) = ProportionalLiquidity.proportionalDeposit(
        curve,
        totalDepositNumeraire
    );
    amountsIn = new uint256[](2);
    amountsIn[0] = amountToDeposit[_getAssetIndex(assetAddresses[0])];
    amountsIn[1] = amountToDeposit[_getAssetIndex(assetAddresses[1])];
    curve.totalSupply = curve.totalSupply + lpTokens;
    BalancerPoolToken._mintPoolTokens(recipient, lpTokens);
    dueProtocolFeeAmounts = new uint256[](2);
    dueProtocolFeeAmounts[0] = 0;
    dueProtocolFeeAmounts[1] = 0;
    _mintProtocolFees();
    emit OnJoinPool(poolId, lpTokens, amountToDeposit);
}
```

## Recommendation
Revise the above routines to ensure the caller must be the BalancerV2 Vault.
