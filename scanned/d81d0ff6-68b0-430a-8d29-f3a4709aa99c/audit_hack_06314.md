# [H] Theft of funds through reentrancy

## Summary
Severity: High
Reporter: minhtrng
Source: https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/ClaimManager/Implementations/ClaimManagerV1.sol#L203-L272
Type: audit-issue

## Details
# Theft of funds through reentrancy

## Summary

A tier winner can steal funds he is not entitled to via reentrancy.

## Vulnerability Detail

The function `ClaimManager.permissionedClaimTieredBounty` allows the winner of a tier to claim his share of the funds. The bounty implementation specific functions `claimTieredFixed` and `claimTiered` both have the `nonReentrant` modifier to prevent reentrancy. However, this only prevents reentrancy through ERC777 tokens or malicious ERC20 contracts, because the `nonReentrant` modifier only prevents nested calls to the function, but once execution has finished, the function can be called again in the same transaction.

This can be abused for both `TieredFixedBounty` and `TieredPercentage` bounty if the winning tier has an NFT attached. The claiming functions both perform the transfer of ERC20s/protocol tokens first and then the transfer of NFTs later:

```js
//_claimTieredFixedBounty, very similar for _claimTieredPercentageBounty
uint256 volume = _bounty.claimTieredFixed(_closer, _tier);
...
for (uint256 i = 0; i < _bounty.getNftDeposits().length; i++) {
    bytes32 _depositId = _bounty.nftDeposits(i);
    if (_bounty.tier(_depositId) == _tier) {
        _bounty.claimNft(_closer, _depositId);
```

If the `_closer` address has been set by the winner to be a malicious contract, the control flow can be taken over (through the `onERC721Received` function) and the function `ClaimManager.permissionedClaimTieredBounty` can be reentered. As a side note, the malicious contract would need to transfer the NFT back into the bounty contract to prevent the call from reverting.

There are checks in place to prevent a tier from claiming more than once. However due to incorrect/missing application of the checks-effects-interactions pattern, the flag is only set at the very end of the function:

```js
//checks claimed flag is not set
_eligibleToClaimTier(_bounty, _tier, _closer);

//also checks claimed flag
uint256 volume = _bounty.claimTieredFixed(_closer, _tier);

//reentrancy through NFTs
...

//actually setting the flag
_bounty.setTierClaimed(_tier);
```

## Impact

Stolen funds

## Code Snippet

https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/ClaimManager/Implementations/ClaimManagerV1.sol#L203-L272

https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/ClaimManager/Implementations/ClaimManagerV1.sol#L278-L341

## Tool used

Manual Review

## Recommendation
Apply the CEI pattern correctly by marking the tier as claimed before transferring any funds. Alternatively, add a nonReentrant modifier to `ClaimManager.permissionedClaimTieredBounty`.
