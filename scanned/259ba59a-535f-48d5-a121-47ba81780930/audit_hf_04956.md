# [M] First depositor can effectively disable the per-

## Summary
Severity: Medium
Contest weight: 0.7030
Dataset id: 22916
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The manager of a Vault can set a performance fee, which will be collected if the overall vault tokens have an appreciated price beyond the previous high water mark. However, the first depositor on a Vault can manipulate that high watermark and set it to a value that will never be reached, effectively disabling the performance fee. Each time a deposit or withdrawal happens on the Vault, the fees are minted to the manager, including the performance fee. This will happen at _mintManagerFee, which will calculate the fee to mint in _availableManagerFee:  
s/PoolLogic.sol#L729  
```solidity
function _mintManagerFee() internal returns (uint256 fundValue) {
    uint256 available = _availableManagerFee(
        fundValue,
        tokenSupply,
        performanceFeeNumerator,
        managerFeeNumerator,
        managerFeeDenominator
    );
}
```
In the _availableManagerFee function, the performance fee will be calculated only if the current token price is higher than the high watermark for the token price (tokenPriceAtLastFeeMint).  
s/PoolLogic.sol#L694  
```solidity
function _availableManagerFee(
    uint256 _fundValue,
    uint256 _tokenSupply,
    uint256 _performanceFeeNumerator,
    uint256 _managerFeeNumerator,
    uint256 _feeDenominator
) internal view returns (uint256 available) {
    if (_tokenSupply == 0 || _fundValue == 0) return 0;
    uint256 currentTokenPrice = _fundValue.mul(10 ** 18).div(_tokenSupply);
    if (currentTokenPrice > tokenPriceAtLastFeeMint) {
        available = currentTokenPrice
            .sub(tokenPriceAtLastFeeMint)
            .mul(_tokenSupply)
            .mul(_performanceFeeNumerator)
            .div(_feeDenominator)
            .div(currentTokenPrice);
    }
}
```
When the Vault is first deployed, the first depositor can manipulate the value of tokenPriceAtLastFeeMint to set it at a value high enough so that the token price will never reach it, effectively disabling the performance fee. The steps to execute the attack are the following:  
1. Deposit little value on the Vault, minting a low amount of shares (e.g. 1e8)  
2. Donate some value directly to the Vault (e.g. 1 DAI)  
3. Call mintManagerFee, which will set tokenPriceAtLastFeeMint at the current token price  
• The token price is calculated as fundValue \* 1e18 / totalSupply, so the resulting token price in this scenario will be 1e28 (1e18 \* 1e18 / 1e8).  
4. After the token price has been stored, withdraw all funds (after the cooldown)  
5. Finally, deposit a normal amount of tokens (e.g. 10 DAI), this will set the current token price at 1e18.  
After this attack sequence, the token price is established at 1e18 for the next users to come, but the high watermark (tokenPriceAtLastFeeMint) has been set at 1e28. This means that in order for the manager to ever collect a performance fee, the token price should be multiplied by 10\^10 times (literally 10 billion times), which is not realistic at all. The first depositor of a Vault can disable the performance fee forever, which translates to a loss of fees for the Vault's manager.

## Recommendation
In order to solve this issue, is recommended to reset the high water mark (tokenPriceAtLastFeeMint) each time the Vault is completely emptied:  
```solidity
function _withdrawTo(
    address _recipient,
    uint256 _fundTokenAmount,
    uint256 _slippageTolerance
) internal nonReentrant whenNotFactoryPaused whenNotPaused {
    require(lastDeposit[msg.sender] < block.timestamp, "can withdraw shortly");
    require(balanceOf(msg.sender) >= _fundTokenAmount, "insufficient balance");
    require(_slippageTolerance <= 10_000, "invalid tolerance");
    // Scoping to avoid "stack-too-deep" errors.
    {
        // Calculating how much pool token supply will be left after withdrawal and
        // whether or not this satisfies the min supply (100_000) check.
        // If the user is redeeming all the shares then this check passes.
        // Otherwise, they might have to reduce the amount to be withdrawn.
        uint256 supplyAfter = totalSupply().sub(_fundTokenAmount);
        require(supplyAfter >= 100_000 || supplyAfter == 0, "below supply threshold");
    }
    // calculate the exit fee
    uint256 fundValue = _mintManagerFee();
    // calculate the proportion
    uint256 portion = _fundTokenAmount.mul(10 ** 18).div(totalSupply());
    if (portion == 1e18) tokenPriceAtLastFeeMint = 1e18;
}
```
