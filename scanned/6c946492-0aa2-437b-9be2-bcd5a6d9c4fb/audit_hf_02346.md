# [M] Incorrect Deposit Share Distribution

## Summary
Severity: Medium
Contest weight: 0.4606
Dataset id: 12732
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the FRPVault contract inherits from the ERC4626Upgradeable of OpenZeppelin and overwrites the mint()/deposit() interfaces to charge a minting fee. While examining the distribution of the new minted shares between the user and the fee recipient, we notice the distribution is incorrect. To elaborate, we show below the code snippet from the FRPVault contact. As the name indicates, the deposit() function is used to deposit _assets amount of assets to the vault and mint the new shares to the _receiver. The deposit() function converts the input _assets to the new shares to be minted. The new shares consists of two parts. One part is minted to the user and the left is minted to the fee recipient as minting fee. The minting fee is charged on top of the shares to be minted to the user. If we assume the shares to the user is A, the minting fee is A*fee with the following equation: A*fee + A = shares. As a result, A = shares/(1+fee), where fee = MINTING_FEE_IN_BP/BP. Moreover, A = (_shares * BP)/ (BP + MINTING_FEE_IN_BP) and the minting fee = A*fee = (_shares * MINTING_FEE_IN_BP)/ (BP + MINTING_FEE_IN_BP). However, the deposit() function directly uses the total shares as the base to calculate the minting fee (line 209). Per our calculation, it shall use (_shares * BP)/ (BP + MINTING_FEE_IN_BP) as the base. What is more, it shares the same issue in the previewDeposit() routine which shall use (_shares * BP)/ (BP + MINTING_FEE_IN_BP) as the base to calculate the minting fee (line 240).

```solidity
/// @inheritdoc ERC4626Upgradeable
function deposit(uint256 _assets, address _receiver) public override returns (uint256) {
    require(_assets <= maxDeposit(_receiver), "FRPVault: deposit more than max");
    // calculate the shares to mint
    uint shares = convertToShares(_assets);
    // charge the actual fees
    _chargeAUMFee();
    uint fee = (shares * MINTING_FEE_IN_BP) / BP;
    if (fee != 0) {
        _mint(feeRecipient, fee);
    }
    _deposit(msg.sender, _receiver, _assets, shares - fee);
    return shares - fee;
}

/// @inheritdoc ERC4626Upgradeable
function previewDeposit(uint256 _assets) public view override returns (uint256) {
    uint shares = super.previewDeposit(_assets);
    uint fee = (shares * MINTING_FEE_IN_BP) / BP;
    // While depositing exact amount of assets user receives shares minus fee payed on that amount
    return shares - fee;
}
```

## Recommendation
Revise the above mentioned deposit()/previewDeposit() to correctly distribute the shares minted to the user and the fee recipient.
