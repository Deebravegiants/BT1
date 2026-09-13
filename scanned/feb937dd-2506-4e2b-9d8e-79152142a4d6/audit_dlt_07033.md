# [M] M-08 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-16
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/52
Type: code-finding

## Details
# Lines of code




# Vulnerability details

Mitigation of M-08: NOT fully mitigated

## Mitigated issue
[M-08: Burner role can not be revoked](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/47)

The issues were that the burner role in GameItems.sol, and the staker role in FighterFarm.sol (see duplicate [#710](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/710)) cannot be revoked.

## Mitigation review - only case of burner role fixed
`setAllowedBurningAddresses()` in GameItems.sol has been replaced by an [`adjustBurningAccess()`](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/1192a55963c92fb4bd9ca8e0453c96af09731235/src/GameItems.sol#L194-L197).

The staker role in FighterFarm.sol still can only be [added](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/1192a55963c92fb4bd9ca8e0453c96af09731235/src/FighterFarm.sol#L151).

### Recommended mitigation steps
Similarly implement an `adjustStakerAccess()` instead for the staker role in FighterFarm.sol.
