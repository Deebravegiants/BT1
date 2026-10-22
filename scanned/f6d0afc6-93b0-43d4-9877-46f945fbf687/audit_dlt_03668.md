# [M] M-05A Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-12
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/17
Type: code-finding

## Details
# Lines of code

https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/setUpAirdrop-mitigation/src/FighterFarm.sol#L241
https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/setUpAirdrop-mitigation/src/FighterFarm.sol#L424


# Vulnerability details

# Lines of code
### Old lines of code
https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/FighterFarm.sol#L214
https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/FighterFarm.sol#L379

### Mitigated lines of code
https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/setUpAirdrop-mitigation/src/FighterFarm.sol#L241
https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/setUpAirdrop-mitigation/src/FighterFarm.sol#L424

# Vulnerability details

The issue was reported in [#1017](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/1017).

It describes 4 impacts:
1. DNA malipulation in [FighterFarm.reRoll()](https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/FighterFarm.sol#L379). It was mitigated in [#16](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/16/commits/255e72b14f124f643003f0cde8eaacaec9ed42e9).
2. DNA malipulation in [FighterFarm.mintFromMergingPool()](https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/FighterFarm.sol#L313). It was mitigate in [#3](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/3/files).
3. DNA malipulation in [FighterFarm.redeemMintPass()](https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/FighterFarm.sol#L233). It was mitigated in [#10](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/10/commits/370b0a02d99d7ade4bd04b9c9b784f56b478e841).
4. DNA malipulation in [FighterFarm.claimFighters()](https://github.com/code-423n4/2024-02-ai-arena/blob/main/src/FighterFarm.sol#L191). It was mitigated in [#11](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/pull/11/commits/03d35bd8522ae07fc84474c32978bd58fa20ecb8).

The M-05A mitigation aims to mitigate 1) and 4).

The vulnerabilities rely on the fact that `dna` depends on an external input that can be used by a malicious
player to obtain rare `fighters`. In detail, in both of them the computation of `dna` depends on `msg.sender`
and other parameters that can foreseen. A malicious player can create many wallet, or could use [Create2](https://docs.alchemy.com/docs/create2-an-alternative-to-deriving-contract-addresses)
to create a contract at wanted address.

# Mitigation applied by developers

```diff
FighterFarm.claimFighters()

@@ -220,7 +220,7 @@ contract FighterFarm is ERC721, ERC721Enumerable {
        for (uint16 i = 0; i < totalToMint; i++) {
            _createNewFighter(
                msg.sender, 
-               uint256(keccak256(abi.encode(msg.sender, fighters.length))),
+               uint256(keccak256(abi.encode(msg.sender, nftsClaimed[msg.sender][0], nftsClaimed[msg.sender][1]))),
                modelHashes[i], 
                modelTypes[i],
                i < numToMint[0] ? 0 : 1,
```

```diff
FighterFarm.reRoll()

@@ -403,7 +403,7 @@ contract FighterFarm is ERC721, ERC721Enumerable {
        bool success = _neuronInstance.transferFrom(msg.sender, treasuryAddress, rerollCost);
        if (success) {
            numRerolls[tokenId] += 1;
-           uint256 dna = uint256(keccak256(abi.encode(msg.sender, tokenId, numRerolls[tokenId])));
+           uint256 dna = uint256(keccak256(abi.encode(tokenId, numRerolls[tokenId])));
            (uint256 element, uint256 weight, uint256 newDna) = _createFighterBase(dna, fighterType);
            fighters[tokenId].element = element;
            fighters[tokenId].weight = weight;
```

# Comment about the Mitigation Proposal
We think this mitigation doesn't solve the initial issue.

### FighterFarm.claimFighters()
It is still possible to forecast the `dna` outcome. When a player uses `FighterFarm.claimFighters()` for the
first time, the values of `nftsClaimed[msg.sender][0]` and `nftsClaimed[msg.sender][1]` are 0. Now,
the malicious player has to build a wallet, i.e., has to find the correct `msg.sender` for the tuple (msg.sender, 0, 0)
to obtain `dna` for a rare `fighter`.
Before the mitigation, the malicious player should obtain the right `fighter.length`. This value could be forced,
but it was a value that didn't depend on player input and it is not fixed. After mitigation, the issue isn't solve.
The situation is even worse. 

### FighterFarm.reRoll()
It is still possible to forecast the `dna` outcome. Furthermore, a malicious player could wait the right
`tokenId`, i.e., he/she could wait to mint a redeem pass until he/she knows it can be obtained a good `tokenId`,
which can be used with a specific `numRerolls` in range [0, `maxRerollsAllowed[fighterType]`] to obtain a rare
`fighter`. Now, `dna` didn't rely anymore on a value supplied by an external source. However, it is still 
possible to force `FighterFarm.reRoll()` to obtain a rare `fighter`

### Conclusion
Thanks to reason above, we think the issue is unmitigated. It is still possible to forecast `fighter` attributes
and force protocol to obtain rare `fighters`. We propose to use an external oracle or to add `block.timestamp`
to `dna` computation to make harder to obtain wanted `dna`


## Assessed type

Other
