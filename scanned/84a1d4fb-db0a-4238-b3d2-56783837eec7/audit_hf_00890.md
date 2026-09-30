# [M] CollVaultRouter::redeemToOne will lead

## Summary
Severity: Medium
Contest weight: 0.5958
Dataset id: 2646
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
CollVaultRouter::redeemToOne() is designed to redeem shares of a collateral vault and swap all reward tokens to a single target one and send it to the redeemer. This works well if the collateral vault does not accrue iBGT rewards. In case it accrues iBGT rewards, those rewards are staked and the collateral vault accounts for the minted iBGTVault shares as reward and when user directly redeem through the collateral vault, those iBGTVault shares would be redeemed and rewards from the iBGTVault would be send directly to the redeemer.
In the case of redeeming through CollVaultRouter only rewards token for the collateral vault which we redeem against would be send to the user. If iBGTVault has different rewards they would become stuck in the CollateralVaultRouter.
Lets go through the workflow of harvesting rewards and the workflow of redeeming shares in a InfraredCollateralVault (excluding iBGTVault from the example as it has slightly different mechanism for rewards accrual).
In InfraredCollateralVault::_harvestRewards() we have an _autoCompoundHook to account for iBGT reward:
```solidity
(rewards, _token) = _autoCompoundHook(_token, _ibgt, _ibgtVault, rewards);
uint fee = rewards * _performanceFee / BP;
uint netRewards = rewards - fee;
if (_token == asset()) {
    iVault.stake(netRewards);
}
// Meanwhile the token doesn't has an oracle mapped, it will be processed as a donation
// This will avoid returns meanwhile a newly Infrared pushed reward token is not mapped
if (_hasPriceFeed(_token) && _token != _iRedToken && !_isCollVault(_token)) {
    _increaseBalance(_token, netRewards);
    // First time the oracle happens to be mapped, we add the token to the rewardedTokens
    // If token has no oracle map this won't be called, hence not DOS the vault at `totalAssets`
    _addRewardedToken(_token); // won't add duplicates
}
```
and in KodiakIslandVault we see the implementation:
```solidity
function _autoCompoundHook(address _token, address _ibgt, IIBGTVault _ibgtVault, uint _rewards) internal override returns (uint, address) {
    uint bbIbgtMinted;
    bool isIBGT = _token == _ibgt;
    if (isIBGT) {
        IERC20(_ibgt).safeIncreaseAllowance(address(_ibgtVault), _rewards);
        bbIbgtMinted = _ibgtVault.deposit(_rewards, address(this));
        _rewards = bbIbgtMinted;
    }
    _token = isIBGT ? address(_ibgtVault) : _token;
    return (_rewards, _token);
}
```
We see that when we have iBGT reward, it is staked into iBGTVault and the minted shares are accounted as a reward token.
When users redeem directly against the collateal vault, there are two internal mechanisms to withdraw the assets:
_withdraw(msg.sender, receiver, _owner, assetAmount, shares);
_withdrawExtraRewardedTokens(receiver, netShares, _totalSupply);
The first one handles the underlying asset of the vault and the second one handles all rewarded tokens.
Taking a look into _withdrawExtraRewardedTokens(), we see that the iBGTVault shares are not directly sent to the redeemer, but they are redeemed and user gets the rewards from iBGTVault.
```solidity
if (token == _ibgtVault && _ibgtVault != address(this)) {
    IInfraredCollateralVault(token).redeem(amount, receiver, address(this));
} else {
    IERC20(token).safeTransfer(receiver, amount);
}
```
In the context of CollVaultRouter, the receiver of all tokens initially is the router:
```solidity
params.collVault.redeem(params.shares, address(this), msg.sender);
```
This means that both reward tokens groups (from the collateral vault which we redeem against and the reward tokens from iBGTVault) will be send to the router but only tokens from the initial collateral vault would be swapped to target token and send to the user because we only construct the tokens array based on the initial collateral vault rewards:
```solidity
address[] memory tokens = params.collVault.tryGetRewardedTokens();
```
/core/vaults/InfraredCollateralVault.sol#L82C1-L129C6 _autoCompoundHook():
blob/main/blockend/src/periphery/CollVaultRouter.sol#L352C1-L393C6
Internal Pre-conditions
Reward tokens of the collateral vault which we redeem against is a subset of the reward tokens for iBGTVault
External Pre-conditions
N/A
Attack Path
Consider the case where:
• KodiakIslandVault has reward tokens A, B and iBGTVault (actually iBGT, but it is staked an accounted as iBGTVault).
• iBGTVault has reward tokens A, B, C.
• User use CollateralVaultRouter::redeemToOne()
– KodiakIslandVault transfers A, B as reward tokens of itself and A, B, C as reward tokens from iBGTVault
– tokens array which is constructed at the beginning of the redeemToOne() workflow will only contain A, B, iBGTVault
– amount of received iBGTVault would be zero because it was internally redeemed for A, B, C
• Only A and B tokens would be swapped to target token which would be send to user, leaving token C stuck.
There is an admin functionality claimLockedTokens which can rescue those stuck funds but there is way for attacker to use those funds before they are saved. In depositFromAny() we separately provide the inputTokenAmount and the dexCalldata and dexCalldata can be arbitrary constructed by users. In normal workflow, it is expected that there are no funds in the router contract and the specified input token amount for the OogaBooga swap will be provided by the user. Attacker can take advantage of the stuck funds and use them for his deposit by specifying an inputAmount for his dexCalldata equal to params.inputAmount + the amount of stuck funds.
This way attacker does not need to provide all the funds used for the actual swap and will utilize the funds that previous redeemers have lost due to the mismatch of reward tokens.
Adding reference for the swap API of OogaBooga Router:
https://docs.oogabooga.io/deployments/aggregator/obrouter-reference
Permanent loss of funds for users using redeemToOne functionality.

## Recommendation
When constructing the tokens array in redeemToOne(), consider using an intersection of the rewards set of both iBGTVault and the collateral vault shares which are redeemed. This is okay solution only if it is sure that the only collateral vault reward which is accepted is iBGTVault.
