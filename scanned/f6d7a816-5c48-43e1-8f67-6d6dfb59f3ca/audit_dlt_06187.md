# [H] Permanent lock NFT and founds for Out of gas

## Summary
Severity: High
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-06
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/8
Type: hats-finding

## Details
**Github username:** @rotcivegaf
**Submission hash (on-chain):** 0xb0e88a5974064e8907631968a8478266bc0f6396ec1ff7456f53196b8a4bfb9d
**Severity:** high

**Description:**
# title: Permanent lock NFT and founds for Out of gas

## Description

In the contract **HoprStakeBase** there are many functions that loop through the `redeemedNft` array, the size of this array grows every time an NFT is locked

The more elements the array has, the more gas these functions will consume, such as the `_unlockFor` function:

https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/8822abcfa5348b8e1f45c1d9fa5a5135090e0622/packages/ethereum/contracts/src/static/stake/HoprStakeBase.sol#L490-L504

This function cannot be executed, because may end up consuming more than the maximum gas per block and the reward funds and NFTs are blocked. It reverts with `OutOfGas`

>> The functions `isNftTypeAndRankRedeemed1`, `isNftTypeAndRankRedeemed2`, `isNftTypeAndRankRedeemed3`, `isNftTypeAndRankRedeemed4`, `_getCumulatedRewardsIncrement` and `_unlockFor` also have this problem

## Proof of Concept (PoC) File

In this PoC we have a length of 50 NFT and consume 2289369 gas, with 100 consume 4518188

Run with `forge test --match-test PoC`: https://gist.github.com/rotcivegaf/8424052955f92d01af387eb879091105

## Recommendation

Define a maximum to lock NFT per account on `onERC721Received` function, for example:

```solidity
@@ -28,6 +28,8 @@ contract HoprStakeBase is Ownable, IERC777Recipient, IERC721Receiver, Reentrancy
     uint256 claimedRewards; // Rewards claimed by the account.
   }
 
+  uint256 constant LOCK_MAXIMUM = 100;
+
   // public constants
   uint256 public constant FACTOR_DENOMINATOR = 1e12; // Denominator of the “Basic reward factor”. Default value is 1e12.
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/8_
