# [M] M-03 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-15
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/29
Type: code-finding

## Details
# Lines of code

https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/fix-47/src/MergingPool.sol#L137-L175


# Vulnerability details

# Lines of code
### Old lines of code
https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/MergingPool.sol#L134-L167

### Mitigated lines of code
https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/fix-47/src/MergingPool.sol#L137-L175

# Vulnerability details
[M-03 (#932)](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/932) reports that `Fighter created by mintFromMergingPool can have arbitrary weight and element`.

[FighterFarm.mintFromMergingPool()](https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/FighterFarm.sol#L307-L331) can be called only by the [MergingPool.claimRewards()](https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/MergingPool.sol#L134-L167) method:

```
MergingPool.sol#L134-L167

134      /// @notice Allows the user to batch claim rewards for multiple rounds.
135      /// @dev The user can only claim rewards once for each round.
136      /// @param modelURIs The array of model URIs corresponding to each round and winner address.
137      /// @param modelTypes The array of model types corresponding to each round and winner address.
138      /// @param customAttributes Array with [element, weight] of the newly created fighter.
139      function claimRewards(
140          string[] calldata modelURIs, 
141          string[] calldata modelTypes,
142          uint256[2][] calldata customAttributes
143      ) 
144          external 
145      {
146          uint256 winnersLength;
147          uint32 claimIndex = 0;
148          uint32 lowerBound = numRoundsClaimed[msg.sender];
149          for (uint32 currentRound = lowerBound; currentRound < roundId; currentRound++) {
150              numRoundsClaimed[msg.sender] += 1;
151              winnersLength = winnerAddresses[currentRound].length;
152              for (uint32 j = 0; j < winnersLength; j++) {
153                  if (msg.sender == winnerAddresses[currentRound][j]) {
154                      _fighterFarmInstance.mintFromMergingPool(
155                          msg.sender,
156                          modelURIs[claimIndex],
157                          modelTypes[claimIndex],
158                          customAttributes[claimIndex]
159                      );
160                      claimIndex += 1;
161                  }
162              }
163          }
164          if (claimIndex > 0) {
165              emit Claimed(msg.sender, claimIndex);
166          }
167      }
```

`MergingPool.claimRewards()` is used to claim rewards, i.e., to mint a new fighter from the merging pool for each round where the player wins. When a player calls `MergingPool.claimRewards()`, he/she can pass the `customAttributes` parameter, which is not checked anywhere. This array is passed to `FighterFarm.mintFromMergingPool()`:

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

This method also doesn't check `customAttributes` parameter and pass it directly to [FighterFarm._createNewFighter()](https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/FighterFarm.sol#L476-L531) which use it to mint a `fighter` with `customAttributes` values for `weight` and `element`:

```
FighterFarm.sol#L484-L506

484      function _createNewFighter(
485          address to, 
486          uint256 dna, 
487          string memory modelHash,
488          string memory modelType, 
489          uint8 fighterType,
490          uint8 iconsType,
491          uint256[2] memory customAttributes
492      ) 
493          private 
494      {  
495          require(balanceOf(to) < MAX_FIGHTERS_ALLOWED);
496          uint256 element; 
497          uint256 weight;
498          uint256 newDna;
499          if (customAttributes[0] == 100) {
500              (element, weight, newDna) = _createFighterBase(dna, fighterType);
501          }
502          else {
503              element = customAttributes[0];
504              weight = customAttributes[1];
505              newDna = dna;
506          }
```

In this way, the player can set directly `weight` and `element` values. This behavior is wanted by developers. However, `weight` and `element` must be bound within the same limit described in [FighterFarm._createFighterBase()](https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/FighterFarm.sol#L462-L474):

```
FighterFarm.sol#L462-L474

470          uint256 element = dna % numElements[generation[fighterType]];
471          uint256 weight = dna % 31 + 65;
```

In other words, `element` must be in the range [0, `numElements[generation[fighterType]]-1`], and `weight` must be in the range [65, 95], extremes included. This vulnerability allows the user to set `weight` and `element` out from this ranges.


# Recommended Mitigation proposed by wardens
Wardens proposed to restrict `weight` and `element` using a check inside `FighterFarm.mintFromMergingPool()`. Developers decided to apply a different mitigation.


# Mitigation applied by developers
To mitigate this issue, developers added two lines to [MergingPool.claimRewards()](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/setUpAirdrop-mitigation/src/MergingPool.sol#L142-L175) method, that is the only one which can call `FighterFarm.mintFromMergingPool()`:

```diff
MergingPool.sol#L142-L175

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
+               require(customAttributes[j][0] < _fighterFarmInstance.numElements(generation), "MergingPool: element out of bounds");
+               require(customAttributes[j][1] >= 65 && customAttributes[j][1] <= 95, "MergingPool: weight out of bounds");
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

These two lines check the values of `customAttributes` passed by the player who is claiming the reward.
[This solution was implemented by the Ai Arena team](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/16/commits/3b2b3fa832f2b82885985c28b886faf680941254)

# Comment about the Mitigation Proposal
We want to report two issues:

### Unmitigated risk
It is still possible to pass `customAttributes` out of bounds. For example, if the maximum value of `winnersLength` is 2 and a player tries to claim 3 rewards, the 3rd will be not checked. The following is a coded POC:

```
function testClaimRewardsCustomAttributesOutOfBound() public {
        address user0 = vm.addr(1);
        address user1 = vm.addr(2);
        address user2 = vm.addr(3);

        _mintFromMergingPool(user0);
        _mintFromMergingPool(user1);
        _mintFromMergingPool(user2);

        uint256 totalRound = 6;


        uint256[] memory _winners013 = new uint256[](2);
        _winners013[0] = 0;
        _winners013[1] = 1;

        uint256[] memory _winners023 = new uint256[](2);
        _winners023[0] = 0;
        _winners023[1] = 2;

        uint256 totalWinUser1 = 0;
        
        for (uint i = 0; i < totalRound; i++) {
            if (i%2 == 0) {
                _mergingPoolContract.pickWinners(_winners013);
                totalWinUser1 += 1;
            } else {
                _mergingPoolContract.pickWinners(_winners023);
            }
        }

        string[] memory _modelURIs = new string[](totalWinUser1);
        string[] memory _modelTypes = new string[](totalWinUser1);
        uint256[2][] memory _customAttributes = new uint256[2][](totalWinUser1);

        _modelURIs[0] = "ipfs://bafybeiaatcgqvzvz3wrjiqmz2ivcu2c5sqxgipv5w2hzy4pdlw7hfox42m";
        _modelTypes[0] = "original";
        _customAttributes[0][0] = uint256(1);
        _customAttributes[0][1] = uint256(80);

        _modelURIs[1] = "ipfs://bafybeiaatcgqvzvz3wrjiqmz2ivcu2c5sqxgipv5w2hzy4pdlw7hfox42m";
        _modelTypes[1] = "original";
        _customAttributes[1][0] = uint256(1);
        _customAttributes[1][1] = uint256(80);

        _modelURIs[2] = "ipfs://bafybeiaatcgqvzvz3wrjiqmz2ivcu2c5sqxgipv5w2hzy4pdlw7hfox42m";
        _modelTypes[2] = "original";
        _customAttributes[2][0] = uint256(10);
        _customAttributes[2][1] = uint256(99);

        vm.startPrank(user1);
        _mergingPoolContract.claimRewards(
            _modelURIs,
            _modelTypes,
            _customAttributes,
            uint32(totalRound - 1)
        );

        uint256 numRewards = _mergingPoolContract.getUnclaimedRewards(user1);
        assertEq(numRewards, 0);

        assertEq(_fighterFarmContract.balanceOf(user1), 4);
    }

Output:
emit FighterCreated(id: 5, weight: 99, element: 10, generation: 0)
```

This happens because a player can claim more rewards than the `winnerLenght`. Furthermore `winnerLenght` changes round by round and is completely unbounded from the number of rewards a player can claim.

### The wrong usage of index forces players to create and pass an array of `customAttributes`
Even if a player wants to claim one reward, he/she has to pass to `MergingPool.claimRewards()` arrays with at least `winnersLength` elements, where `winnersLength` is the maximum value among `winnerAddresses[round].length` for analyzed rounds (i.e. rounds in the selected interval). We reported this issue with `Low` severity.

### Our mitigation proposal
We suggest to change these two lines:

```diff
@@ -156,9 +156,9 @@ contract MergingPool is ReentrancyGuard{
             numRoundsClaimed[msg.sender] += 1;
             winnersLength = winnerAddresses[currentRound].length;
             for (uint32 j = 0; j < winnersLength; j++) {
-                require(customAttributes[j][0] < _fighterFarmInstance.numElements(generation), "MergingPool: elemen
t out of bounds");
-                require(customAttributes[j][1] >= 65 && customAttributes[j][1] <= 95, "MergingPool: weight out of b
ounds");
                 if (msg.sender == winnerAddresses[currentRound][j]) {
+                    require(customAttributes[claimIndex][0] < _fighterFarmInstance.numElements(generation), "
MergingPool: element out of bounds");
+                    require(customAttributes[claimIndex][1] >= 65 && customAttributes[claimIndex][1] <= 95, "
MergingPool: weight out of bounds");
                     _fighterFarmInstance.mintFromMergingPool(
                         msg.sender,
                         modelURIs[claimIndex],
```

We also suggest to implement a public function to obtain the number of `rewards` a player can claim within a specified interval of rounds:

```
    function getClaimRewardsAmount(
        uint32 totalRoundsToConsider
    ) 
        external nonReentrant returns (uint32 claimAmount)
    {
        uint256 winnersLength;
        uint32 lowerBound = numRoundsClaimed[msg.sender];
        require(lowerBound + totalRoundsToConsider < roundId, "MergingPool: totalRoundsToConsider exceeds the limit");
        for (uint32 currentRound = lowerBound; currentRound < lowerBound + totalRoundsToConsider; currentRound++) {
            numRoundsClaimed[msg.sender] += 1;
            winnersLength = winnerAddresses[currentRound].length;
            for (uint32 j = 0; j < winnersLength; j++) {
                if (msg.sender == winnerAddresses[currentRound][j]) {
                    claimAmount += 1;
                }
            }
        }
    }
```

In this way, a player can easily know the length of parameters he/she should pass to the `MergingPool.claimRewards()` method.

### Conclusion
We consider this issue unmitigated because it is still possible to create a `fighter` with `weight` and `element` values out of bounds.





## Assessed type

Invalid Validation
