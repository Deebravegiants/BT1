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

        eETH.mintShares(msg.sender, share); ///<----------------- @audit 

        return share;
    }
```


According to the "[Minting and burning `eETH`](https://etherfi.gitbook.io/etherfi/ether.fi-whitepaper/introduction#minting-and-burning-eeth)" in the documentation, a staker who holds T-NFTs is supposed to be able to deposit them (T-NFTs) into the liquidity pool and mint the eETH equivalent to the value of the T-NFT like this:

> When a staker deposits ETH into the pool, the pool mints eETH tokens and transfers them to the depositor. A staker who holds T-NFTs can deposit them into the liquidity pool and mint the eETH equivalent to the value of the T-NFT (determined via an oracle.) 

Based on above, within the LiquidityPool#`deposit()` and the LiquidityPool#`_deposit()`, the deposit logic for not only a staker who just deposits ETH but also a staker who is a T-NFT holder and deposit their T-NFT is supposed to be implemented.

However, within the LiquidityPool#`deposit()` and the LiquidityPool#`_deposit()` (To be precise, within all of the Ether.Fi's contracts that is in-scope), there is no logic for a staker who holds T-NFTs to deposit their T-NFTs into the Liquidity Pool. 


## Impact
This lead to that a staker who holds T-NFTs can **not** deposit them into the liquidity pool and mint the eETH equivalent to the value of the T-NFT.


## Recommendation 
Within the LiquidityPool#`deposit()`, consider adding the `isDepositingTNFT` as a parameter in order to separate the subsequent processing depends on which asset (Native ETH or T-NFT) a staker deposits like this:
```diff
    // Used by eETH staking flow
+   function deposit(bool isDepositingTNFT) external payable returns (uint256) {
-   function deposit() external payable returns (uint256) {
+       return deposit(address(0), isDepositingTNFT); 
-       return deposit(address(0)); 
    }
```
```diff
+   function deposit(address _referral, bool isDepositingTNFT) public payable whenNotPaused returns (uint256) {
-   function deposit(address _referral) public payable whenNotPaused returns (uint256) {
        require(_isWhitelisted(msg.sender), "Invalid User"); 

        emit Deposit(msg.sender, msg.value, SourceOfFunds.EETH, _referral);

+       return _deposit(isDepositingTNFT);
-       return _deposit();
    }
```

Then, within the LiquidityPool#`_deposit()`, consider separating subsequent processing depends on that the deposited-asset is Native ETH or T-NFT (the `isDepositingTNFT` would be `true` / `false`).
If the deposited-asset is T-NFT (the `isDepositingTNFT` would be `true`), these three steps should be done:
1/ A T-NFT would be transferred from the T-NFT holder.
2/ The equivant value of tNFT-transferred in ETH (by using Oracle) would be calculated.
3/ The equivant value of tNFT-transferred in ETH would be used to calculate the `shares` and the `totalValueInLp`.

```diff
+   function _deposit(bool isDepositingTNFT) internal returns (uint256) {
-   function _deposit() internal returns (uint256) {

+       uint256 share; 

+       If (isDepositingTNFT == true) {
+           /// 1. A T-NFT would be transferred from the T-NFT holder.
+           tNFT.safeTransferFrom(msg.sender, address(this), tokenId);
+
+           /// 2. The equivant value of tNFT-transferred in ETH (by using Oracle) would be calculated.
+           uint256 tNFTValueInETH = T_NFT_VALUE_IN_ETH_RETRIEVED_VIA_ORACLE;

+           /// 3. The equivant value of tNFT-transferred in ETH would be used to calculate the shares and the totalValueInLp.
+           totalValueInLp += uint128(tNFTValueInETH);
+           uint256 share = _sharesForDepositAmount(tNFTValueInETH);
+       } else {
+           totalValueInLp += uint128(msg.value);
+           uint256 share = _sharesForDepositAmount(msg.value);
+           if (msg.value > type(uint128).max || msg.value == 0 || share == 0) revert InvalidAmount();
+       }

-       totalValueInLp += uint128(msg.value);
-       uint256 share = _sharesForDepositAmount(msg.value);
-       if (msg.value > type(uint128).max || msg.value == 0 || share == 0) revert InvalidAmount();

        eETH.mintShares(msg.sender, share);

        return share;
    }
```
(TODO：At the line of `uint256 tNFTValueInETH = T_NFT_VALUE_IN_ETH_RETRIEVED_VIA_ORACLE` above, the logic to calculate the equivant value of tNFT-transferred in ETH by using Oracle should be implemented and the `T_NFT_VALUE_IN_ETH_RETRIEVED_VIA_ORACLE` should be replaced with it)
