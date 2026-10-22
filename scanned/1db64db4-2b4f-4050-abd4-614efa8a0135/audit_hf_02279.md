# [M] Inconsistent Logics to Calculate callerFeeAmount

## Summary
Severity: Medium
Contest weight: 0.5936
Dataset id: 12467
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The WombatStaking contract interacts with the Wombat Exchange to provide functionalities such as adding new liquidity, staking LP tokens on MasterWombat, and staking WOM to get veWom. With the accumulated veWom, the MagpieV2 protocol can vote the Wom emission on Wombat and receive bribe rewards. The MagpieV2 protocol allows for the vlMGP holders to vote on how the veWom voting powers are distributed to each Wombat LP. To incentivize the caller to cast the pending votes to Wombat, it rewards the caller with a caller fee from the Wombat bribe rewards.

To elaborate, we show below the code snippet of the WombatStaking::Vote() routine. As the name indicates, it is used to vote the Wom emission on Wombat and receive bribe rewards. For each received bribe reward, it calculates protocol fee first (line 386), decreases the protocol fee from the reward amount (line 390), and then calculates the caller fee based on the new reward amount (line 393).
```solidity
function vote(
    address[] calldata _lpVote,
    int256[] calldata _deltas,
    address[] calldata _rewarders,
    address caller
) external returns (IERC20[][] memory rewardTokens, uint256[][] memory callerFeeAmounts) {
    if (msg.sender != bribeManager)
        revert OnlyBribeMamager();
    if (_lpVote.length != _rewarders.length)
        revert LengthMismatch();
    Public
    uint256[][] memory rewardAmounts = voter.vote(_lpVote, _deltas);
    rewardTokens = new IERC20[][](rewardAmounts.length);
    callerFeeAmounts = new uint256[][](rewardAmounts.length);
    for (uint256 i; i < rewardAmounts.length; i++) {
        address bribesContract = address(voter.infos(_lpVote[i]).bribe);
        if (bribesContract != address(0)) {
            rewardTokens[i] = IWombatBribe(bribesContract).rewardTokens();
            callerFeeAmounts[i] = new uint256[](rewardAmounts[i].length);
            for (uint256 j; j < rewardAmounts[i].length; j++) {
                uint256 rewardAmount = rewardAmounts[i][j];
                uint256 callerFeeAmount = 0;
                if (rewardAmount > 0) {
                    uint256 protocolFee = (rewardAmount * bribeProtocolFee) / DENOMINATOR;
                    if (protocolFee > 0) {
                        IERC20(rewardTokens[i][j]).safeTransfer(bribeFeeCollector, protocolFee);
                        rewardAmount -= protocolFee;
                    }
                    if (caller != address(0) && bribeCallerFee != 0) {
                        callerFeeAmount = (rewardAmount * bribeCallerFee) / DENOMINATOR;
                        IERC20(rewardTokens[i][j]).safeTransfer(bribeManager, callerFeeAmount);
                        rewardAmount -= callerFeeAmount;
                    }
                    IERC20(rewardTokens[i][j]).safeApprove(_rewarders[i], rewardAmount);
                    IBaseRewardPool(_rewarders[i]).queueNewRewards(rewardAmount, address(rewardTokens[i][j]));
                }
                callerFeeAmounts[i][j] = callerFeeAmount;
            }
        }
    }
    return (rewardTokens, callerFeeAmounts);
}
```
Moreover, the WombatStaking contract provides the pendingBribeCallerFee() routine to facilitate the calculation of the caller fee for the pending bribe rewards. However, it comes to our attention that the caller fee is calculated directly based on the original bribe rewards amount (line 226) retrieved from Wombat and it does not take the protocol fee into consideration as in the Vote() routine. As a result, the caller fee amount calculation here is inconsistent with the calculation in the Vote() routine.
```solidity
Public
function pendingBribeCallerFee(address[] calldata pendingPools)
    external
    view
    returns (IERC20[][] memory rewardTokens, uint256[][] memory callerFeeAmount)
{
    // Warning: Arguments do not take into account repeated elements in the pendingPools list
    uint256[][] memory pending = voter.pendingBribes(pendingPools, address(this));
    rewardTokens = new IERC20[][](pending.length);
    callerFeeAmount = new uint256[][](pending.length);
    for (uint256 i; i < pending.length; i++) {
        rewardTokens[i] = IWombatBribe(voter.infos(pendingPools[i]).bribe).rewardTokens();
        callerFeeAmount[i] = new uint256[](pending[i].length);
        for (uint256 j; j < pending[i].length; j++) {
            if (pending[i][j] > 0) {
                callerFeeAmount[i][j] = (pending[i][j] * bribeCallerFee) / DENOMINATOR;
            }
        }
    }
    return (rewardTokens, callerFeeAmount);
}
```

## Recommendation
Revisit the above mentioned Vote()/pendingBribeCallerFee() routines to use the same algorithm for the caller fee calculation.
