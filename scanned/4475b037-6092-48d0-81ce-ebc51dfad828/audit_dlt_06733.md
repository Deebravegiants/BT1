# [M] Contract `PhiNFT1155` can't be paused

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-08-phi
Published: 2024-09-06
Source: https://github.com/code-423n4/2024-08-phi-findings/issues/268
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-08-phi/blob/8c0985f7a10b231f916a51af5d506dd6b0c54120/src/art/PhiNFT1155.sol#L21-L31


# Vulnerability details

## Impact

The pausing mechanism of `PhiNFT1155` contract is implemented incorrectly and doesn't work: users are still able to transfer NFTs in paused state.

## Summary

Contract `PhiNFT1155` inherits from the [following parent contracts](https://github.com/code-423n4/2024-08-phi/blob/8c0985f7a10b231f916a51af5d506dd6b0c54120/src/art/PhiNFT1155.sol#L21-L31):

```solidity
contract PhiNFT1155 is
    Initializable,
    UUPSUpgradeable,
    ERC1155SupplyUpgradeable,
    ReentrancyGuardUpgradeable,
    PausableUpgradeable,
    Ownable2StepUpgradeable,
    IPhiNFT1155,
    Claimable,
    CreatorRoyaltiesControl
{
```

The problem with the above is that inheriting from `PausableUpgradeable` is not effective in the scope of OZ `ERC1155` contracts. As a result, users are able to transfer NFT tokens even when the contract is paused, as the below PoC demonstrates.

## Proof of Concept

Drop this test to [PhiFactory.t.sol](https://github.com/code-423n4/2024-08-phi/blob/8c0985f7a10b231f916a51af5d506dd6b0c54120/test/PhiFactory.t.sol#L163) and execute via `forge test --match-test Kuprum`

```solidity
function testKuprum_PhiNFT1155PauseNotWorking() public {
    _createArt(ART_ID_URL_STRING);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-08-phi-findings/issues/268_
