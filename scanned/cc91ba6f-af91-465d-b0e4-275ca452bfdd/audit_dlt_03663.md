# [M] Players can exploit `mintFromMergingPool` dna calculation to mint rare fighter

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-18
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/68
Type: code-finding

## Details
# Lines of code

https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/FighterFarm.sol#L349-L373


# Vulnerability details

# Players can exploit `mintFromMergingPool` dna calculation to mint rare fighter

## Impact
This issue is strongly related to [issue #1017 - Users can get benefited from DNA pseudorandomly calculation](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/1017).
It describes 4 impacts:
1. DNA malipulation in [FighterFarm.reRoll()](https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/FighterFarm.sol#L379). It was mitigated in [#16](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/16/commits/255e72b14f124f643003f0cde8eaacaec9ed42e9).
2. DNA manipulation in [FighterFarm.mintFromMergingPool()](https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/FighterFarm.sol#L313)
3. DNA malipulation in [FighterFarm.redeemMintPass()](https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/FighterFarm.sol#L233). It was mitigated in [#10](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/10/commits/370b0a02d99d7ade4bd04b9c9b784f56b478e841).
4. DNA malipulation in [FighterFarm.claimFighters()](https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/FighterFarm.sol#L191). It was mitigated in [#11](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/11/commits/03d35bd8522ae07fc84474c32978bd58fa20ecb8).

We want to focus on 2. In [issue #1017] is reported:

```
In this case, the DNA is computed by the msg.sender (in this case will always be 
the _mergingPoolAddress so it is not manipulable) and the number of existing fighters.

In this function a user can not manipulate the output hash, however, he can compute the hash for the upcoming fighters, 
because when a new fighter will be created, the fighters.length will change along with the output hash. As a result, 
a user can claim the MergingPool reward to mint and NFT when the output hash will be benefitial for him.
```

So, before mitigation, `a user can not manipulate the output hash`, but `can claim the MergingPool reward to mint and NFT when the output hash will be benefitial for him`.

Attempted mitigation was made in [#3](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/3/files):

```
@@ -321,7 +321,7 @@ contract FighterFarm is ERC721, ERC721Enumerable {
        require(msg.sender == _mergingPoolAddress);
        _createNewFighter(
            to, 
-           uint256(keccak256(abi.encode(msg.sender, fighters.length))), 
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/68_
