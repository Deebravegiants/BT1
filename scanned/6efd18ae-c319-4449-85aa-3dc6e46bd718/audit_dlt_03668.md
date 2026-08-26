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
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/17_
