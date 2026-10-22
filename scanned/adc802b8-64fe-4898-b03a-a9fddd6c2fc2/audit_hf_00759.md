# [M] Incorrect reward distribution due to feeShares minting order

## Summary
Severity: Medium
Contest weight: 0.5979
Dataset id: 2349
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function claimRewards() public virtual {
    _nonReentrantOn();

    _updateLastTotalAssets(_accrueFee());
    _claimRewards();

    _nonReentrantOff();
}
```
```solidity
function _accrueFee() internal virtual returns (uint256 newTotalAssets) {
    uint256 feeShares;
    (feeShares, newTotalAssets) = _accruedFeeShares();

    if (feeShares != 0) _mint(feeRecipient, feeShares);

    emit EventsLib.AccrueInterest(newTotalAssets, feeShares);
}
```
```solidity
/// @dev Computes and returns the fee shares (`feeShares`) to mint and the new vault's total assets
/// (`newTotalAssets`).
function _accruedFeeShares() internal view virtual returns (uint256 feeShares, uint256 newTotalAssets) {
    newTotalAssets = totalAssets();

    uint256 totalInterest = UtilsLib.zeroFloorSub(newTotalAssets, lastTotalAssets);
    if (totalInterest != 0 && fee != 0) {
        // It is acknowledged that `feeAssets` may be rounded down to 0 if `totalInterest * fee < WAD`.
        uint256 feeAssets = totalInterest.mulDiv(fee, WAD);
        // The fee assets is subtracted from the total assets in this calculation to compensate for the fact
        // that total assets is already increased by the total interest (including the fee assets).
        feeShares = _convertToSharesWithTotals(
            feeAssets,
            totalSupply(),
            newTotalAssets - feeAssets,
            Math.Rounding.Floor
        );
    }
}
```
```solidity
function _update(address _from, address _to, uint256 _value) internal virtual override {
    // on deposit, claim must be first action, new user should not get reward

    // on withdraw, claim must be first action, user that is leaving should get rewards
    // immediate deposit-withdraw operation will not abused it, because before deposit all rewards will be
    // claimed, so on withdraw on the same block no additional rewards will be generated.

    // transfer shares is basically withdraw->deposit, so claiming rewards should be done before any state changes

    _claimRewards();

    super._update(_from, _to, _value);

    if (_value == 0) return;

    _afterTokenTransfer(_from, _to, _value);
}
```
The current implementation distributes rewards _before_ minting fee shares, resulting in the fee recipient receiving shares but no rewards for the corresponding interest accrual period. This creates an inconsistency where the exisiting share owners receive higher than deserved portion of rewards.

Let’s assume Bob is the sole shareholder. What’s happening right now is:

  * Bob deposits at `t` and receives `100%` shares (for simplicity let’s ignore, for now, the `DECIMALS_OFFSET` strategy deployed by the protocol to thwart the first-depositor attack).
  * At some time, `t2`, we see that yield & reward has accrued.
  * Someone calls [claimRewards()](https://github.com/code-423n4/2025-03-silo-finance/blob/main/silo-vaults/contracts/SiloVault.sol#L495) which first internally calls `_updateLastTotalAssets(_accrueFee())` and then `_claimRewards()`:
        
        File: silo-vaults/contracts/SiloVault.sol
        
        495:              function claimRewards() public virtual {
        496:                  _nonReentrantOn();
        497:          
        498:@--->             _updateLastTotalAssets(_accrueFee());
        499:@--->             _claimRewards();
        500:          
        501:                  _nonReentrantOff();
        502:              }

  * [_accrueFee() internally calls _mint()](https://github.com/code-423n4/2025-03-silo-finance/blob/main/silo-vaults/contracts/SiloVault.sol#L946) if `feeShares != 0`.
        
        942:              function _accrueFee() internal virtual returns (uint256 newTotalAssets) {
        943:                  uint256 feeShares;
        944:                  (feeShares, newTotalAssets) = _accruedFeeShares();
        945:          
        946:@--->             if (feeShares != 0) _mint(feeRecipient, feeShares);
        947:          
        948:                  emit EventsLib.AccrueInterest(newTotalAssets, feeShares);
        949:              }

  * Note that `_accruedFeeShares()` on L944 is a **_retrospective way_** to calculate the `feeShares` which should correspond to the `feeAssets` amount applied on the accumulated interest. This is done because the total assets have already grown between `t` and `t2`. This is evident from the `newTotalAssets - feeAssets` term inside [_accruedFeeShares()](https://github.com/code-423n4/2025-03-silo-finance/blob/main/silo-vaults/contracts/SiloVault.sol#L951-L969) and also the comments on L960-961:
        
        951:              /// @dev Computes and returns the fee shares (`feeShares`) to mint and the new vault's total assets
        952:              /// (`newTotalAssets`).
        953:              function _accruedFeeShares() internal view virtual returns (uint256 feeShares, uint256 newTotalAssets) {
        954:                  newTotalAssets = totalAssets();
        955:          
        956:                  uint256 totalInterest = UtilsLib.zeroFloorSub(newTotalAssets, lastTotalAssets);
        957:                  if (totalInterest != 0 && fee != 0) {
        958:                      // It is acknowledged that `feeAssets` may be rounded down to 0 if `totalInterest * fee < WAD`.
        959:                      uint256 feeAssets = totalInterest.mulDiv(fee, WAD);
        960:@--->                 // The fee assets is subtracted from the total assets in this calculation to compensate for the fact
        961:@--->                 // that total assets is already increased by the total interest (including the fee assets).
        962:                      feeShares = _convertToSharesWithTotals(
        963:                          feeAssets,
        964:                          totalSupply(),
        965:@--->                     newTotalAssets - feeAssets,
        966:                          Math.Rounding.Floor
        967:                      );
        968:                  }
        969:              }

This means that the fee recipient is going to be minted the `feeShares` currently because they have a rightful claim to the `feeAssets` which started to accrue right from timestamp `t`.

With that in mind, let’s see the remaining steps -

  * On L946 `_accrueFee() --> _mint()` internally calls the [overridden _update()](https://github.com/code-423n4/2025-03-silo-finance/blob/main/silo-vaults/contracts/SiloVault.sol#L985) function, which in turn calls `_claimRewards()` before `super._update()` actually mints these `feeShares` and increases `totalSupply()`. As the inline code comments explain, this is meant to be a safeguard and it is required so that rewards can be claimed before a new deposit/withdraw/transfer:
        
        976:              function _update(address _from, address _to, uint256 _value) internal virtual override {
        977:                  // on deposit, claim must be first action, new user should not get reward
        978:          
        979:                  // on withdraw, claim must be first action, user that is leaving should get rewards
        980:                  // immediate deposit-withdraw operation will not abused it, because before deposit all rewards will be
        981:                  // claimed, so on withdraw on the same block no additional rewards will be generated.
        982:          
        983:                  // transfer shares is basically withdraw->deposit, so claiming rewards should be done before any state changes
        984:          
        985:@--->             _claimRewards();
        986:          
        987:                  super._update(_from, _to, _value);
        988:          
        989:                  if (_value == 0) return;
        990:          
        991:                  _afterTokenTransfer(_from, _to, _value);
        992:              }

In this case however, what it means is that the **entire** reward is doled out to Bob since he possesses `100%` of shares because the `feeShares` are yet to be minted. By the time the control reaches the second call to `_claimRewards()` on [L499](https://github.com/code-423n4/2025-03-silo-finance/blob/main/silo-vaults/contracts/SiloVault.sol#L499) after minting of these shares, there are no more rewards left to be distributed to the fee recipient.

  * The shares of the fee recipient will now only receive any future rewards and miss out on the current one even though the shares have been rightly minted to them retrospectively. Conversely put, Bob receives more than his fair share of rewards.
  * Note that this is not just a one-time loss of rewards for the fee recipient. Each time `claimRewards()` is called and there is a pending yield to be collected, `feeShares` minted in that cycle lose out on the rewards being distributed. They only get to see a portion of the rewards from the next cycle onwards.

## Recommendation
The current logic of calling `_claimRewards()` from inside `_update()` is correct and works well for all the other cases, so no issues there. For cases where `feeShares` are being minted, however, we may need to introduce additional logic inside `_claimRewards()` which checks for this via a new flag and calculates the reward portion after accounting for these retrospectively minted `feeShares`.

**edd (Silo Finance) acknowledged**
