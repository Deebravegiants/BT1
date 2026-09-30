# [M] Incorrect Redeem Share Distribution

## Summary
Severity: Medium
Contest weight: 0.4605
Dataset id: 12728
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The FRPVault contract inherits from the ERC4626Upgradeable of OpenZeppelin and overwrites the redeem()/withdraw() interfaces to charge a burning fee. While examining the shares distribution between the user and the fee recipient, we notice the distribution is incorrect. To elaborate, we show below the code snippet from the FRPVault contact. As the name indicates, the redeem() function is used to redeem _shares amount of shares from the _owner and transfer the underlying assets to the _receiver. The input _shares consists of two parts. One part could be withdrawn to the user and the left is charged as the burning fee to the fee recipient. The burning fee is charged on top of the shares to be withdrawn to the user. If we assume the shares withdrawn to the user is A, the burning fee is computed as A*fee with the following equation: A*fee + A = _shares. As a result, A = _shares/(1+fee), where fee = BURNING_FEE_IN_BP/BP. We can further derive A = (_shares * BP)/ (BP + BURNING_FEE_IN_BP) and the burning fee = A*fee = (_shares * BURNING_FEE_IN_BP)/ (BP + BURNING_FEE_IN_BP). However, the redeem() function directly uses the input _shares to calculate the burning fee (line 178). Per our calculation, it shall use (_shares * BP)/ (BP + BURNING_FEE_IN_BP) as the base to calculate the burning fee. What is more, it shares the same issue in the previewRedeem() routine where the burning fee is calculated based on the input _shares, not expected (_shares * BP)/ (BP + BURNING_FEE_IN_BP) (line 228).

```solidity
/// @inheritdoc IERC4626Upgradeable
function redeem(
    uint256 _shares,
    address _receiver,
    address _owner
) public
override
returns (uint256) {
    require(_shares <= maxRedeem(_owner), "FRPVault: redeem more than max");
    // previewReedem is fine to use here since we are dealing with exact input of shares so we calculate burning fee on that
    uint256 assetsMinusFee = previewRedeem(_shares);
    uint fee = _chargeBurningFee(_shares, _owner);
    // burns _shares - fee since fee is transferred to the feeRecipient
    _withdraw(msg.sender, _receiver, _owner, assetsMinusFee, _shares - fee);
    return assetsMinusFee;
}

/// @inheritdoc IERC4626Upgradeable
function previewRedeem(uint256 _shares) public view override returns (uint256) {
    // amount of assets received reduced by the shares amount
    return convertToAssets(_shares - (_shares * BURNING_FEE_IN_BP) / BP);
}
```

## Recommendation
Revise the above mentioned redeem()/previewRedeem() to correctly distribute the shares between the user and the fee recipient.
