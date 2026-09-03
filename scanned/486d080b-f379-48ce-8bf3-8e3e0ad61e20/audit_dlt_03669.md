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


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/16_
