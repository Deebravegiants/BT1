# [M] Incorrect implementation of the slippage pa-

## Summary
Severity: Medium
Contest weight: 0.5947
Dataset id: 22915
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There's a slippage parameter on withdrawals that allows users to set a tolerance value on the difference between the owned assets and the actual received assets. to revert even when the slippage doesn't surpass the tolerance set by the user. Each time a user wants to withdraw from the Vault, it receives the underlying assets pro-rata to that user's ownership of the Vault. Given that some underlying assets are deposited in protocols to earn yield (e.g. Aave), withdrawing them will cause some slippage because there are some swaps involved and it depends on the current prices of the assets. For the above reason, there's a slippage parameter in the withdrawal functions that allows users to specify their tolerance to slippage. However, this slippage  
Here's the withdrawal function, which calls the function _withdrawProcessing for each asset to be withdrawn, passing the slippage parameter:  
s/PoolLogic.sol#L373  
```solidity
function _withdrawTo(
    address _recipient,
    uint256 _fundTokenAmount,
    uint256 _slippageTolerance
) internal nonReentrant whenNotFactoryPaused whenNotPaused {
    for (uint256 i = 0; i < _supportedAssets.length; i++) {
        (address asset, uint256 portionOfAssetBalance, bool externalWithdrawProcessed) = _withdrawProcessing(
            _supportedAssets[i].asset,
            _recipient,
            portion,
            _slippageTolerance
        );
    }
}
```
And at the end of the _withdrawProcessing, it checks if the slippage is higher than the tolerance allowed by the user:  
s/PoolLogic.sol#L464  
```solidity
function _withdrawProcessing(
    address asset,
    address to,
    uint256 portion,
    uint256 slippageTolerance
)
internal
returns (
    address, // withdrawAsset
    uint256, // withdrawBalance
    bool externalWithdrawProcessed
)
{
    // Ensure that actual value of tokens transferred is not less than the expected value, corrected by allowed tolerance
    require(
        IPoolManagerLogic(poolManagerLogic).assetValue(withdrawAsset, withdrawBalance) >=
        params.expectedWithdrawValue.mul(10_000 - slippageTolerance).div(10_000),
        "high withdraw slippage"
    );
}
return (withdrawAsset, withdrawBalance, externalWithdrawProcessed);
```
withdrawn amount as a whole, some scenarios will arise where a withdrawal gets tolerance value set by the user. For example, a user wants to withdraw from a Vault and set a maximum slippage of 2%. The Vault has 2 assets equally split, some WETH and a position in Aave. The withdrawal of WETH has a slippage of 0%, and the Aave withdrawal experiences a slippage of 3%. The slippage on the whole withdrawal results in 1.5% so that means that the withdrawal shouldn't revert because the allowed slippage is 2%. However, withdrawn value, this withdrawal will actually revert because the slippage in Aave (3%) has been higher than the tolerance (2%). DoS on withdrawals due to an incorrect implementation of the slippage parameter. The withdrawal function is considered time-sensitive because the value received won't be the same depending on the time given that the overall value of the Aave position is based on the current token prices. Because of that, this issue should

## Recommendation
In order to mitigate this issue, is recommended to check the slippage against the will solve the scenario described above where a withdrawal reverted even if the slippage was lower than the maximum allowed.
