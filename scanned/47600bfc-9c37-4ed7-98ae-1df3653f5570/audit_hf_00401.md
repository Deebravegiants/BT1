# [M] Fee distribution will be DOS'd

## Summary
Severity: Medium
Contest weight: 0.1860
Dataset id: 1787
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Whenever the vaultManager distributes fees it attempts to call _distributeCollectedFeeShares. VaultManager.sol#L642-L652 function _distributeCollectedFeeShares(address _tranche) internal { ITranche(_tranche).maxRedeem(address(this)), address(this), address(this) ); if (assets > 0) { _distributeVeRewards(IVeTranche(ITranche(_tranche).veTranche()), assets); } } We see above that it will always attempt to redeem from the tranche. Tranche.sol#L288-L305 function _withdraw( address caller, address receiver, address owner, uint256 assets, uint256 shares ) internal virtual override { uint256 fee = getWithdrawalFeesRaw(assets); super._withdraw(caller, receiver, owner, assets, shares); if (fee > 0) { SafeERC20.safeTransfer(ERC20(asset()), address(vaultManager), fee); vaultManager.allocateRewards(fee, false); emit FeeTransferredToVM(fee, false); } require(utilizationRatio() < withdrawThreshold, "UTILIZATION_RATIO_MAX"); <- ,→ } The problem here is that L304 reverts when utilizationRatio() < withdrawThreshold, hence all distributions will fail. VaultManager:L643 always redeems shares even if maxRedeem = 0 Internal pre-conditions utilizationRatio >= withdrawThreshold External pre-conditions None Attack Path 1. Fees are ready to be distributed 2. utilizationRatio >= withdrawThreshold for one of the tranches 3. Fee distributions will always revert Fee distribution will be DOS'd

## Recommendation
Redeem should be skipped if maxRedeem returns as 0
