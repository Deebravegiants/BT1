# [M] FighterFarm.reRoll() method works wrong and allows minting wanted attributes

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-12
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/16
Type: code-finding

## Details
# Lines of code

https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/setUpAirdrop-mitigation/src/FighterFarm.sol#L412-L436


# Vulnerability details

# Impact
Each `fighter` has a specific number of max reRolls, according to `fighterType`. This means that the owner of the `fighter` can call `FighterFarm.reRoll()` at most `maxRerollsAllowed` times, in order to obtain better fighter's attributes.

We want to underline three aspects:

* `FighterFarm.reRoll()` operation has a cost in NRN
* `numRerolls` of a specific `fighter` is not reset when it is transfered
* `dna` is the only value used to compute `fighter`'s traits. After [mitigation](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/11/commits/255e72b14f124f643003f0cde8eaacaec9ed42e9), `dna` depends just on `tokenId` and `numRerolls[tokenId]`

Because the reasons above, the owner of a `fighter` can always forecast what is the best number of `reRolls`.
So, a cunning player should always improve its `fighter`'s traits using the right number of `reRolls`. For this reason, we could expect that all `fighters` will be reRolled until they reach the best number of `reRolls`.
Furthermore, a malicious player can wait for the right `tokenId` which can be used in `reRoll` operation to obtain a very rare fighter.

### Remaining reRolls of a fighter don't increase its value
We asked in a private thread a clarification on the `FighterFarm.reRoll()` mechanism. This was the answer:

```
I: I've another question on reRoll method. A fighter can be reRolled several times. 
The limit is the MasRerollsAllowed value. When a fighter is transferred from a player to other,
the numRerolls value is not reset. This means that the onwer can't reRoll the receive fighter, if
the previous owner used all roll changes. Also this is a wanted behavior?

Dev: Yes this is intended. You can think of this as someone potentially paying a premium for an NFT that has 
more reRolls remaining. They should be intrinsically more valuable since they have more optionality.
```

While this was true before the mitigation, now the `dna` doesn't depend on `msg.sender` anymore. This means that the outcomes of `reRoll` operations made by the seller is the same of the outcomes obtained by the buyer. If they are both cunning players, they know before the transfer if that `fighter` would improve using `FighterFarm.reRoll()` operation or not.
We want to underline that this mechanism strongly changes after the mitigation. As long as the outcome of `reRoll` operation depended on `msg.sender`, buying a `fighter` with remaining `reRoll` operations made sense, because buyer `reRoll` operations would have different outcome then the seller ones.

After mitigation, seller and buyer can reach the same rare attributes. They both should be aware on the best outcome of `reRoll` operation. If not, it could happen because one or both of them are not cunning: the transfer could be not fair, impacting the game and the market.

So, after mitigation, the `reRoll` operation appears as a pretense to pay NRNs. Its initial aim is lost.

### The only right thing to do is to reach the best `numRerolls` for each `fighter`
As we said above, remaining reRolls of a fighter don't increase its market value. So, why a player should decide to not perform `reRoll` operations until reaching the best attributes combination? In this way, each player is forced to use NRNs to reach the best combination, because it doens't make sense to have a non-optimal `fighter`: it hasn't more market value and it can become a better `fighter` for sure.

### A malicious player could wait the right `tokenId` to mint its `fighter` and `reRoll` it
A malicious player could wait to redeem his/her mint pass until he can obtain the wanted `tokenId`. This can be done because that player has foreseen that the wanted `tokenId` combined with a specific `numRerolls` permit obtaining a very rare `fighter`.

### Conclusion
Now, the `reRoll` operation seems useless. It can be used only to have different battle traits (weight and element). So we propose `reRoll` modifies just the battle attributes. 

If somebody would sell his/her `fighter`, remaining `numRerolls` doesn't influence the `fighter` value. Before mitigation, there was the possibility that a new player with the right `msg.sender` would obtain better attrbutes for a `fighter`. Now, all players can obtain the same and foreseenable outcome from `reRoll` operations. Furthermore, now malicious players have the possibility to precompute `dna` despite their `msg.sender` and thus they can create `fighter` with wanted rare attributes.

# Proof of concept

This is the mitigated [FighterFarm.reRoll()](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/setUpAirdrop-mitigation/src/FighterFarm.sol#L412-L436) operation:

```
/// @notice Rolls a new fighter with random traits.
/// @param tokenId ID of the fighter being re-rolled.
/// @param fighterType The fighter type.
function reRoll(uint256 tokenId, uint8 fighterType) public {
    require(msg.sender == ownerOf(tokenId));
    require(numRerolls[tokenId] < maxRerollsAllowed[fighterType]);
    require(_neuronInstance.balanceOf(msg.sender) >= rerollCost, "Not enough NRN for reroll");


    _neuronInstance.approveSpender(msg.sender, rerollCost);
    bool success = _neuronInstance.transferFrom(msg.sender, treasuryAddress, rerollCost);
    if (success) {
        numRerolls[tokenId] += 1;
        uint256 dna = uint256(keccak256(abi.encode(tokenId, numRerolls[tokenId])));
        (uint256 element, uint256 weight, uint256 newDna) = _createFighterBase(dna, fighterType);
        fighters[tokenId].element = element;
        fighters[tokenId].weight = weight;
        fighters[tokenId].physicalAttributes = _aiArenaHelperInstance.createPhysicalAttributes(
            newDna,
            generation[fighterType],
            fighters[tokenId].iconsType,
            fighters[tokenId].dendroidBool
        );
        _tokenURIs[tokenId] = "";
    }
}    
```

The `dna` is computed at line [FighterFarm.sol#L424](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/setUpAirdrop-mitigation/src/FighterFarm.sol#L424):

```
            uint256 dna = uint256(keccak256(abi.encode(tokenId, numRerolls[tokenId])));
```

It depends just on `tokenId`, which never change, and `numRerolls[tokenId]`, which can change only using `FighterFarm.reRoll()` operation.

Let's `maxRerollsAllowed[fighterType] = 10`. This means this fighter can be rerolled 10 times. We can forecast the `dna` results for each of 10 reroll operations. For example, we forecast that the 5th `reRolled` operation will reach the best attributes combination. So, we know before the first `reRoll` operation that it not makes sense to perform more than 5 `reRolls`.

If this `fighter` can not reach a good attributes combination, we could try to sell it, hoping we find a naive buyer, with all `numRerolls` available. On the other hand, if this `fighter` can reach a good attributes combination, we could make 5 `reRolls`, obtain the optimal attributes combination and use it in battles; or we could sell it, even before use 5 `reRolls`, because the reachable optimal attributes combination can be forecast by everyone, and it becomes an intrinsic value of the `fighter`


## Tools Used
Visual inspection

## Recommended Mitigation Steps
The issue relies on the pseudorandom mechanism. It is impossible to build a pseudorandom public mechanism that can't be forecasted. Before the mitigation, an external source could be exploited to obtain the wanted `reRoll` outcomes. Now, the best outcome is intrinsic in `fighter`. Furthermore, a malicious player could still exploit the `tokenId` to obtain the wanted `reRoll`. We strongly suggest to use an external oracle or to add `block.timestamp` to the computation of `dna`, to make a bit harder to forecast outcome attributes.








## Assessed type

Other
