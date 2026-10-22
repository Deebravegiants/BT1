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
322          _createNewFighter(
323              to, 
324              uint256(keccak256(abi.encode(msg.sender, fighters.length))), 
325              modelHash, 
326              modelType,
327              0,
328              0,
329              customAttributes
330          );
331      }
```

This function can be called only by the `merging pool contract`. This means that `msg.sender` must be `_mergingPoolAddress`.
However, `msg.sender` is also used as `dna` parameter of `_createNewFighter()` (line [L324](https://github.com/code-423n4/2024-02-ai-arena/blob/cd1a0e6d1b40168657d1aaee8223dc050e15f8cc/src/FighterFarm.sol#L324)). 

**Impact**: Even if an attacker can't exploit this bad randomness to obtain better fighters, players could forecast the attributes of fighters that will be created in the future, due to the bad randomness caused by this issue.

# Recommended Mitigation proposed by wardens
The mitigation proposal is to replace `msg.sender` in line [L324](https://github.com/code-423n4/2024-02-ai-arena/blob/cd1a0e6d1b40168657d1aaee8223dc050e15f8cc/src/FighterFarm.sol#L324) with the address `to`, that should represents the player who calls [MergingPool.claimRewards()](https://github.com/code-423n4/2024-02-ai-arena/blob/cd1a0e6d1b40168657d1aaee8223dc050e15f8cc/src/MergingPool.sol#L139-L167):

```diff
FighterFarm.sol#L307-L331

/// @notice Mints a new fighter from the merging pool.
/// @dev Only the merging pool contract address is authorized to call this function.
/// @param to The address that the new fighter will be assigned to.
/// @param modelHash The hash of the ML model associated with the fighter.
/// @param modelType The type of the ML model associated with the fighter.
/// @param customAttributes Array with [element, weight] of the newly created fighter.
function mintFromMergingPool(
    address to, 
    string calldata modelHash, 
    string calldata modelType, 
    uint256[2] calldata customAttributes
) 
    public 
{
    require(msg.sender == _mergingPoolAddress);
    _createNewFighter(
        to, 
-       uint256(keccak256(abi.encode(msg.sender, fighters.length))),
+       uint256(keccak256(abi.encode(to, fighters.length))), 
        modelHash, 
        modelType,
        0,
        0,
        customAttributes
    );
}
```

[This solution was implemented by the Ai Arena team](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/3/commits/6d38b3cb03ff2cb2a27ea346d27588143fb893f4)

# Comment about the Mitigation Proposal
This finding belongs to a group of issues that reported the low randomness of dna. Two of the most important are [#53](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/53) and [#519](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/519). The root cause is that `msg.sender` can be a bad source of randomness because an attacker could create a malicious contract at the wanted address using, for example, [Create2](https://docs.alchemy.com/docs/create2-an-alternative-to-deriving-contract-addresses).

In the case above, before the mitigation, nobody could exploit the vulnerability, because the `msg.sender` value was always the `_mergingPoolAddress`. After the mitigation, the `dna` of the new fighter relies on the caller's address. So, the mitigation could introduce the possibility of manipulating the `msg.sender` address and obtaining wanted attributes.

### Attack vector
Let's think that before the current round, `fighters.length` into [FighterFarm.sol](https://github.com/code-423n4/2024-02-ai-arena/blob/cd1a0e6d1b40168657d1aaee8223dc050e15f8cc/src/FighterFarm.sol#L69) is 0. Eve locally tries many combinations and finds that the tuple `(address_E, fighters.length=3)` permits creating a very rare fighter: Eve can forecast this is because she can exploit the line [FighterFarm.sol#214](https://github.com/code-423n4/2024-02-ai-arena/blob/cd1a0e6d1b40168657d1aaee8223dc050e15f8cc/src/FighterFarm.sol#L214):

```
FighterFarm.sol#214

214                  uint256(keccak256(abi.encode(msg.sender, fighters.length))),
```

to obtain `dna` and then use its value to precompute the new fighter's physical attributes:

```
FighterFarm.sol#L510-L515

510          FighterOps.FighterPhysicalAttributes memory attrs = _aiArenaHelperInstance.createPhysicalAttributes(
511              newDna,
512              generation[fighterType],
513              iconsType,
514              dendroidBool
515          );
```

Now, Eve creates a new contract at `address_E` and tries to win the current round (for example using a new fighter redeemed with a mint pass).
If she wins, she could call `MergingPool.claimRewards()` just after someone else has obtained the fighter number 3 (in other words, when fighters.length=3).

We know this attack vector could be hard to perform, but we have to report the consequences of mitigation. To solve the bad randomness introduced by this mitigation, we propose to implement something like [FighterFarm.redeemMintPass()](https://github.com/code-423n4/2024-02-ai-arena/blob/cd1a0e6d1b40168657d1aaee8223dc050e15f8cc/src/FighterFarm.sol#L233) where the `dna` is obtained from an external source (for example, from a backend server) and cannot be manipulated by the caller.


### Conclusions
In conclusion, the proposed mitigation solves the initial bad randomness due to too little `dna` combinations space. However, it doesn't solve the issue reported by [#1017](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/1017):

```
In this function a user can not manipulate the output hash, however, he can compute the hash for the upcoming fighters, 
because when a new fighter is created, the fighters.length will change along with the output hash. As a result, 
a user can claim the MergingPool reward to mint and NFT when the output hash will be benefitial for him.
```

The malicious user can still forecast the outcome fighter attributes and claim the MergingPool reward when it is more convenient for him/her. Furthermore, it introduces the possibility to manipulate the `msg.sender` value to obtain a wanted `dna` and, so, a fighter with wanted valuable and rare attributes. We are going to report this comment as "unmitigated" and the attack vector above as a "new finding".


## Assessed type

Other
