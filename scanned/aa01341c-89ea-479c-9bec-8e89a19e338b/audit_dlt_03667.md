# [M] M-05B Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-13
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/18
Type: code-finding

## Details
# Lines of code

https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/setUpAirdrop-mitigation/src/FighterFarm.sol#L366


# Vulnerability details

# Lines of code

### Old lines of code
https://github.com/code-423n4/2024-02-ai-arena/blob/cd1a0e6d1b40168657d1aaee8223dc050e15f8cc/src/FighterFarm.sol#L324

### Mitigated lines of code
https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/setUpAirdrop-mitigation/src/FighterFarm.sol#L366

# Vulnerability details
The issue was reported in [#578](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/578) and [#1017](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/1017).

The vulnerability is inside [FighterFarm.mintFromMergingPool()](https://github.com/code-423n4/2024-02-ai-arena/blob/cd1a0e6d1b40168657d1aaee8223dc050e15f8cc/src/FighterFarm.sol#L307-L331):

```
FighterFarm.sol#L307-L331

307      /// @notice Mints a new fighter from the merging pool.
308      /// @dev Only the merging pool contract address is authorized to call this function.
309      /// @param to The address that the new fighter will be assigned to.
310      /// @param modelHash The hash of the ML model associated with the fighter.
311      /// @param modelType The type of the ML model associated with the fighter.
312      /// @param customAttributes Array with [element, weight] of the newly created fighter.
313      function mintFromMergingPool(
314          address to, 
315          string calldata modelHash, 
316          string calldata modelType, 
317          uint256[2] calldata customAttributes
318      ) 
319          public 
320      {
321          require(msg.sender == _mergingPoolAddress);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/18_
