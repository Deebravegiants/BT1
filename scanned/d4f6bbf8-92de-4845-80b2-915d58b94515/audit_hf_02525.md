# [M] stake() functions calculate the incentive based on the token balance not with the amount to be staked

## Summary
Severity: Medium
Contest weight: 0.6003
Dataset id: 13515
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`stake()` function in the three staking vaults calculates the incentive based on the total balance of the tokens instead of the actual balance that is going to be staked.

For example: in `BlazeStakingVault.stakeBlaze()`: the incentive is calculated based on the available blaze balance, then this incentive is deducted from the available balance to get the `blazeToStake`, then this value is checked to be greater than `minStakeAmount` and less than `maxStakeAmount`, so if it's less than the maximum limit; `blazeToStake` is updated to equal that maximum limit:
```solidity
function stakeBlaze() external onlyByOwnerInPrivateMode {
    State storage _state = state;
    uint256 blazeToStake = blaze.balanceOf(_this());
    uint256 incentive = wmul(blazeToStake, state.incentive);
    blazeToStake -= incentive;
    require(_state.lastStakeTs != 0 || blazeToStake >= _state.minStakeAmount, CooldownNotPassed());
    require(
        block.timestamp - _state.lastStakeTs >= _state.stakingCooldown
        || blazeToStake >= _state.minStakeAmount,
        CooldownNotPassed()
    );
    if (blazeToStake > _state.maxStakeAmount) blazeToStake =
    Phoenix_report.md
    _state.maxStakeAmount;
    blazeStaking.stakeBlaze(blazeToStake, BLAZE_MAX_STAKE);
    blaze.transfer(msg.sender, incentive);
    emit Staked(++_state.lastStakingPosition, blazeToStake);
    _state.lastStakeTs = uint32(block.timestamp);
}
```
So as can be noticed, the incentive sent to the user for calling `blazeStake()` can be much larger than intended if the initial `blazeToStake` is greater than `maxStakeAmount` as the incentive is calculated based on the total balance and not based on the updated `blazeToStake` amount; resulting in sending the user a large incentive than intended.

Same issue in `FluxStakingVault.stake()` & `TitanXStakingVault.stake()` functions.

## Recommendation
Calculate the incentive based on the final `blazeToStake` that's going to be staked :
```solidity
function stakeBlaze() external onlyByOwnerInPrivateMode {
    State storage _state = state;
    uint256 blazeToStake = blaze.balanceOf(_this());
    require(_state.lastStakeTs != 0 || blazeToStake >= _state.minStakeAmount, CooldownNotPassed());
    require(
        block.timestamp - _state.lastStakeTs >= _state.stakingCooldown
        || blazeToStake >= _state.minStakeAmount,
        CooldownNotPassed()
    );
    if (blazeToStake > _state.maxStakeAmount) blazeToStake =
    _state.maxStakeAmount;
    uint256 incentive = wmul(blazeToStake, state.incentive);
    blazeToStake -= incentive;
    require(blazeToStake >= _state.minStakeAmount);
    blazeStaking.stakeBlaze(blazeToStake, BLAZE_MAX_STAKE);
    blaze.transfer(msg.sender, incentive);
    Phoenix_report.md
    emit Staked(++_state.lastStakingPosition, blazeToStake);
    _state.lastStakeTs = uint32(block.timestamp);
}
```
