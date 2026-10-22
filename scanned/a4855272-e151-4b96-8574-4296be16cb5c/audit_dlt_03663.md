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
+           uint256(keccak256(abi.encode(to, fighters.length))), 
            modelHash, 
            modelType,
            0,
```

We think that this mitigation doesn't solve the issue. Furthermore, it introduces a new vulnerability. Now,
the user can `manipulate the output hash`, because it depends on the `to` address, which can be manipulated by
the user.

## Proof of Concept
The PoC of this issue is similar to the ones in [#53](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/53) and [#519](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/519).

After mitigation, the attributes of the fighter obtained using the [FighterFarm.mintFromMergingPool()](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/FighterFarm.sol#L349-L373)
depends on two parameters:

```
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
        uint256(keccak256(abi.encode(to, fighters.length))), 
        modelHash, 
        modelType,
        0,
        0,
        customAttributes
    );
}
```

The value passed to [line L366](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/FighterFarm.sol#L366) represents the `dna`.
It depends on the `to` address and the `fighters.length`.

`FighterFarm.mintFromMergingPool()` can be called successfully just by the contract at `_mergingPoolAddress`, i.e., [MergingPool.sol](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/setUpAirdrop-mitigation/src/MergingPool.sol),
using the [MergingPool.claimRewards()](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/MergingPool.sol#L137-L175) method:

```
/// @notice Allows the user to batch claim rewards for multiple rounds.
/// @dev The user can only claim rewards once for each round.
/// @param modelURIs The array of model URIs corresponding to each round and winner address.
/// @param modelTypes The array of model types corresponding to each round and winner address.
/// @param customAttributes Array with [element, weight] of the newly created fighter.
function claimRewards(
    string[] calldata modelURIs, 
    string[] calldata modelTypes,
    uint256[2][] calldata customAttributes,
    uint32 totalRoundsToConsider
) 
    external nonReentrant
{
    uint256 winnersLength;
    uint32 claimIndex = 0;
    uint32 lowerBound = numRoundsClaimed[msg.sender];
    require(lowerBound + totalRoundsToConsider < roundId, "MergingPool: totalRoundsToConsider exceeds the limit");
    uint8 generation = _fighterFarmInstance.generation(0);
    for (uint32 currentRound = lowerBound; currentRound < lowerBound + totalRoundsToConsider; currentRound++) {
        numRoundsClaimed[msg.sender] += 1;
        winnersLength = winnerAddresses[currentRound].length;
        for (uint32 j = 0; j < winnersLength; j++) {
            require(customAttributes[j][0] < _fighterFarmInstance.numElements(generation), "MergingPool: element out of bounds");
            require(customAttributes[j][1] >= 65 && customAttributes[j][1] <= 95, "MergingPool: weight out of bounds");
            if (msg.sender == winnerAddresses[currentRound][j]) {
                _fighterFarmInstance.mintFromMergingPool(
                    msg.sender,
                    modelURIs[claimIndex],
                    modelTypes[claimIndex],
                    customAttributes[claimIndex]
                );
                claimIndex += 1;
            }
        }
    }
    if (claimIndex > 0) {
        emit Claimed(msg.sender, claimIndex);
    }
}
```

So, a player can `mintFromMerginPool` only when he/she claims a reward after he/she wins a battle.

Let's explain the attack vector. Before the next round, `fighter.length = 0`. Eve was able to forecast that a very rare
fighter can be minted using a specific address, called `address_E`, and when `fighter.length = 10`. She can do that
because she can precompute the `dna` value, and use [AiArenaHelper.createPhysicalAttributes()](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/setUpAirdrop-mitigation/src/AiArenaHelper.sol#L78-L121)
to forecast the outcome attributes.

Using [Create2](https://docs.alchemy.com/docs/create2-an-alternative-to-deriving-contract-addresses), Eve can create a malicious
contract at address `address_E`. Then Eve mints a new fighter using, for example, a mint pass and tries to win the
current round. If she manages to do that, she can use the contract at address `address_E` to claim a reward at the current
round. 

Assuming that after this round, `fighter.length = 0` still holds. The malicious contract could implement a call to
`MergingPool.claimRewards()` that is called continuously and reverts until `fighter.length = 10`.

In this way, Eve is sure to claim a reward with `address_E` and `fighter.length = 10`, and thus obtain the fighter
with wanted characteristics.

## Tools Used
Visual inspection

## Recommended Mitigation Steps
The problem relies on the usage of an external controlled input by a pseudorandom algorithm. We suggest introducing
an oracle to obtain random input numbers, or at least to use `block.timestamp`, to make harder to forecast when
the `fighter.length` reaches the wanted value:

```diff
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
-       uint256(keccak256(abi.encode(to, fighters.length))), 
+       uint256(keccak256(abi.encode(to, fighters.length, block.timestamp))), 
        modelHash, 
        modelType,
        0,
        0,
        customAttributes
    );
}
```


## Assessed type

Other
