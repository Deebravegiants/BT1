# [M] LenderCommitmentGroup pools will have incor-

## Summary
Severity: Medium
Contest weight: 0.5928
Dataset id: 22730
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LenderCommitGroup_Smart contract incorporates internal accounting for the amount of tokens deposited, withdrawn, etc. The problem is that if one of the pools has a fee-on-transfer token, the accounting is not adjusted. This will create inflated accountings of the tokens within the pool, and impact the exchange rate. LenderCommitmentGroup_Smart is a contract that acts as it's own loan committment, which has liquidity pools with principal token and collateral token. Users can deposit principal tokens in exchange for share tokens. Here is the flow of depositing principal tokens for shares:
```solidity
LenderCommitmentGroup_Smart::addPrincipalToCommitmentGroup
function addPrincipalToCommitmentGroup(
    uint256 _amount,
    address _sharesRecipient
) external returns (uint256 sharesAmount_) {
    principalToken.transferFrom(msg.sender, address(this), _amount);
    sharesAmount_ = _valueOfUnderlying(_amount, sharesExchangeRate());
    totalPrincipalTokensCommitted += _amount;
    poolSharesToken.mint(_sharesRecipient, sharesAmount_);
}

function sharesExchangeRate() public view virtual returns (uint256 rate_) {
    uint256 poolTotalEstimatedValue = getPoolTotalEstimatedValue();
    if (poolSharesToken.totalSupply() == 0) {
        return EXCHANGE_RATE_EXPANSION_FACTOR; // 1 to 1 for first swap
    }
    rate_ = (poolTotalEstimatedValue * EXCHANGE_RATE_EXPANSION_FACTOR) / poolSharesToken.totalSupply();
}

function _valueOfUnderlying(
    uint256 amount,
    uint256 rate
) internal pure returns (uint256 value_) {
    if (rate == 0) {
        return 0;
    }
    value_ = (amount * EXCHANGE_RATE_EXPANSION_FACTOR) / rate;
}
```
As you can see, the original _amount entered is used to not only issue the shares, but to keep track of the amount pool has:
```solidity
function getPoolTotalEstimatedValue()
    public
    view
    returns (uint256 poolTotalEstimatedValue_)
{
    int256 poolTotalEstimatedValueSigned = int256(
        totalPrincipalTokensCommitted
    ) +
    int256(totalInterestCollected) +
    int256(tokenDifferenceFromLiquidations) -
    int256(totalPrincipalTokensWithdrawn);
    poolTotalEstimatedValue_ = poolTotalEstimatedValueSigned > int256(0)
        ? uint256(poolTotalEstimatedValueSigned)
        : 0;
}
```
If poolTotalEstimatedValue is inflated, then the exchange rate will be incorrect. As mentioned above, incorrect exchange rate calculation. Users will not receive the correct amount of shares/PT when withdrawing/depositing.

## Recommendation
Check balance before and after transferring, then update accounting.
