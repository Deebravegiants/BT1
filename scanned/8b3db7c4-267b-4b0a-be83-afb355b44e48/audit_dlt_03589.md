# [M] M-02 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-pooltogether-mitigation
Published: 2023-08-21
Source: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/24
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-vault/blob/main/src/Vault.sol#L1397
https://github.com/GenerationSoftware/pt-v5-claimer/blob/main/src/Claimer.sol#L163


# Vulnerability details

## Comments

In the previous implementation a malicious user could set arbitrary vault hooks for `afterClaimPrize` and `beforeClaimPrize` that could be used to gas grief the claimer or cause other claims in the same call to fail by deliberately reverting

## Mitigation
The referenced PR does solve the original issue by capping the gas sent to external calls and safely catching reverts. I was slightly concerned that enough gas was being passed to the hooks for a single reentrant call to frontrun a prize claim, however this has been fixed by another change where previously claimed prizes safely return 0. However this mitigation is unresolved by another change.

## Persisting issue
There was another change made to the repo where claiming logic was simplified and mainly moved out of the Vault contract. However with this change any reverts are not being safely caught:

```
function _claim(
    Vault _vault,
    uint8 _tier,
    address[] calldata _winners,
    uint32[][] calldata _prizeIndices,
    address _feeRecipient,
    uint96 _feePerClaim
  ) internal returns (uint256) {
    uint256 actualClaimCount;
    uint256 winnersLength = _winners.length;
    for (uint256 w = 0; w < winnersLength; w++) {
      uint256 prizeIndicesLength = _prizeIndices[w].length;
      for (uint256 p = 0; p < prizeIndicesLength; p++) {
        if (0 != _vault.claimPrize(
          _winners[w],
          _tier,
          _prizeIndices[w][p],
          _feePerClaim,
          _feeRecipient
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/24_
