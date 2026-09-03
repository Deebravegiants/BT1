# [M] Lack of a deposit logic for a staker who holds T-NFTs to be able to deposit them (T-NFTs) into the liquidity pool and mint the eETH equivalent to the value of the T-NFT

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-12
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/50
Type: hats-finding

## Details
**Github username:** @0xmuxyz
**Twitter username:** --
**Submission hash (on-chain):** 0x2cb39ef7bf3b72e93caa2dec259e9a59981ef8ed05e5a852eb2243e04bd808a4
**Severity:** medium

**Description:**
## Description
Within the LiquidityPool#`deposit()`, the LiquidityPool#`deposit()` that can specify the `_referral` would be called like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/LiquidityPool.sol#L147
```solidity
    // Used by eETH staking flow
    function deposit() external payable returns (uint256) {
        return deposit(address(0));  ///<--------- @audit
    }
```

Then, within the LiquidityPool#`deposit()` that can specify the `_referral`, the LiquidityPool#`_deposit()` would be called like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/LiquidityPool.sol#L155
```solidity
    function deposit(address _referral) public payable whenNotPaused returns (uint256) {
        require(_isWhitelisted(msg.sender), "Invalid User"); 

        emit Deposit(msg.sender, msg.value, SourceOfFunds.EETH, _referral);

        return _deposit(); ///<--------- @audit
    }
```

Within the LiquidityPool#`_deposit()`, the `totalValueInLp` and the `share` would be calculated.
Then, the amount (`share`) of eETH would be minted to the caller (`msg.sender`) like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/LiquidityPool.sol#L572-L573 \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/LiquidityPool.sol#L576
```solidity
    function _deposit() internal returns (uint256) {
        totalValueInLp += uint128(msg.value); ///<----------------- @audit 
        uint256 share = _sharesForDepositAmount(msg.value); ///<----------------- @audit 
        if (msg.value > type(uint128).max || msg.value == 0 || share == 0) revert InvalidAmount();

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/50_
