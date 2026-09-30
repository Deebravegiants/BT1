# [M] Incorrect fee share calculation in harvest function

## Summary
Severity: Medium
Contest weight: 0.5765
Dataset id: 6333
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the current implementation of the harvest() function, fee shares are calculated as a percentage of the existing token supply:
```solidity
uint256 currentSupply = totalSupply();
sharesMinted = currentSupply.mulDiv($.feeRateBps, BPS_DIVIDER, Math.Rounding.Floor);
```
This approach doesn't properly calculate the correct proportion of fee shares to mint. When new shares are minted, the total supply increases, but the fee calculation doesn't account for these new shares in the total. For a fee rate of f, the correct proportion of new shares relative to the post-mint total supply should be f/(1-f) of the total. The current implementation simply mints f of the pre-mint total, which results in less than f of the post-mint total being fee shares. This means the protocol is earning fewer fees than intended according to the fee rate.

Impact Explanation:
The impact is medium. The treasury receives fewer fee shares than it should based on the intended fee rate. This effectively reduces the protocol's fee income and benefits existing token holders at the expense of the treasury. The magnitude of this issue increases with higher fee rates.

## Recommendation
Modify the harvest() function to correctly calculate the fee shares relative to the post-mint total:
```solidity
function harvest()
    external
    whenNotPaused
    nonReentrant
    returns (uint256 sharesMinted)
{
    WrappedDollarVaultStorageV0 storage $ = _wrappedDollarVaultStorageV0();
    if (!$.registryAccess.hasRole(VAULT_HARVESTER_ROLE, _msgSender())) {
        revert NotAuthorized();
    }
    if (block.timestamp < $.lastHarvestTimestamp + ONE_DAY) {
        revert HarvestTooFrequent();
    }
    uint256 currentSupply = totalSupply();
    // Calculate fee shares using formula fS/(1-f) to get the correct proportion
    sharesMinted = currentSupply.mulDiv(
        $.feeRateBps,
        BPS_DIVIDER - $.feeRateBps,
        Math.Rounding.Ceil
    );
    if (sharesMinted == 0) revert ZeroAmount();
    $.lastHarvestTimestamp = block.timestamp;
    _mint($.treasury, sharesMinted);
    emit Harvested(_msgSender(), sharesMinted);
    return sharesMinted;
}
```
