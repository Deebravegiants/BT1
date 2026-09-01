# [H] Vault's don't verify that a strategy's deadline has passed

## Summary
Severity: High
Chain: Smart contract
Component: 2023-01-astaria
Published: 2023-01-11
Source: https://github.com/code-423n4/2023-01-astaria-findings/issues/122
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-01-astaria/blob/main/src/VaultImplementation.sol#L229-L266
https://github.com/code-423n4/2023-01-astaria/blob/main/src/AstariaRouter.sol#L439


# Vulnerability details

## Impact
The vault doesn't verify that a deadline hasn't passed when a commitment is validated. Users are able to take out loans using strategies that have already expired. Depending on the nature of the strategy that can cause a loss of funds for the LPs.

## Proof of Concept
When you take out a loan using the AstariaRouter, the deadline is verified:
```sol
  function _validateCommitment(
    RouterStorage storage s,
    IAstariaRouter.Commitment calldata commitment,
    uint256 timeToSecondEpochEnd
  ) internal view returns (ILienToken.Lien memory lien) {
    if (block.timestamp > commitment.lienRequest.strategy.deadline) {
      revert InvalidCommitmentState(CommitmentState.EXPIRED);
    }
// ...
```
But, `VaultImplementation._validateCommitment()` skips that check:
```sol
  function _validateCommitment(
    IAstariaRouter.Commitment calldata params,
    address receiver
  ) internal view {
    uint256 collateralId = params.tokenContract.computeId(params.tokenId);
    ERC721 CT = ERC721(address(COLLATERAL_TOKEN()));
    address holder = CT.ownerOf(collateralId);
    address operator = CT.getApproved(collateralId);
    if (
      msg.sender != holder &&
      receiver != holder &&
      receiver != operator &&
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-01-astaria-findings/issues/122_
