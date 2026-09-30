# [M] Incorrect missing Amount to Withdraw from Splitter

## Summary
Severity: Medium
Contest weight: 0.4537
Dataset id: 13241
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Tetu v2 protocol, the TetuVaultV2 contract is a customized ERC4626 vault. Users deposits will be buffered in the vault, and after the defined buffer is filled, the remaining assets are invested to the splitter. User can withdraw directly from the vault if it has enough assets to cover the buffer and the withdrawal amount. Or the missing part will be withdrawn from the splitter to the vault. While examining the calculation of the missing amount, we notice the missing amount calculation needs to be improved.
To elaborate, we show below the _processWithdrawFromSplitter() routine. As the name indicates, it is used to calculate for the withdrawal amount from the splitter and move assets to the vault. Firstly, the routine uses current buffer amount to calculate the desired withdrawal amount from the splitter. By design, it shall use the new buffer amount which is the total asset amount subtracting the desired withdrawal amount of the user. What's more, it doesn't subtract the available asset public amount in the vault from the missing amount. As a result, more assets than expected are withdrawn from the splitter.
```solidity
function _processWithdrawFromSplitter(
    uint assetsNeed,
    uint shares,
    uint totalSupply_,
    uint _buffer,
    ISplitter _splitter,
    uint assetsInVault
) internal
    // withdraw everything from the splitter accurately check the share value
    if (shares == totalSupply_)
        _splitter.withdrawAllToVault();
    else
        uint assetsInSplitter = _splitter.totalAssets();
        // we should always have buffer amount inside the vault
        uint missing = (assetsInSplitter + assetsInVault) - _buffer / BUFFER_DENOMINATOR + assetsNeed;
        missing = Math.min(missing, assetsInSplitter);
        // if zero should be resolved splitter side
        _splitter.withdrawToVault(missing);
```

## Recommendation
Revise current execution logic of _processWithdrawFromSplitter() to withdraw the exact desired amount of assets from the splitter.
