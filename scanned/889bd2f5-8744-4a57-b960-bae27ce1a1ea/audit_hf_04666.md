# [M] Malicious users could block liquidation or per-

## Summary
Severity: Medium
Contest weight: 0.4651
Dataset id: 22411
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation uses a "push" approach where reward tokens are sent to the recipient during every update, which introduces additional attack surfaces that the attackers can exploit. An attacker could intentionally affect the outcome of the transfer to gain a certain advantage or carry out certain attack. The worst-case scenario is that malicious users might exploit this trick to intentionally trigger a revert when someone attempts to liquidate their unhealthy accounts to block the liquidation, leaving the protocol with bad debts and potentially leading to insolvency if it accumulates. We are extending this functionality to allow nTokens to be incentivized by a secondary reward token. On Arbitrum, this will be ARB as a result of the ARB STIP grant. In the future, this may be any arbitrary ERC20 token. Line 231 of the _claimRewards function below might revert due to various issues such as:
• tokens with blacklisting features such as USDC (users might intentionally get into the blacklist to achieve certain outcomes)
• tokens with hook, which allow the target to revert the transaction intentionally
• unexpected error in the token's contract
File: SecondaryRewarder.sol
216:
```solidity
function _claimRewards(address account, uint256 nTokenBalanceBefore, uint256 nTokenBalanceAfter) private {
    uint256 rewardToClaim = _calculateRewardToClaim(account, nTokenBalanceBefore, accumulatedRewardPerNToken);

    // Precision here is:
    // nTokenBalanceAfter (INTERNAL_TOKEN_PRECISION)
    // accumulatedRewardPerNToken (INCENTIVE_ACCUMULATION_PRECISION)
    // DIVIDE BY
    // INTERNAL_TOKEN_PRECISION
    // => INCENTIVE_ACCUMULATION_PRECISION (1e18)
    rewardDebtPerAccount[account] = nTokenBalanceAfter
        .mul(accumulatedRewardPerNToken)
        .div(uint256(Constants.INTERNAL_TOKEN_PRECISION))
        .toUint128();

    if (0 < rewardToClaim) {
        GenericToken.safeTransferOut(REWARD_TOKEN, account, rewardToClaim);
        emit RewardTransfer(REWARD_TOKEN, account, rewardToClaim);
    }
}
```
If a revert occurs, the following functions are affected:
_claimRewards -> claimRewardsDirect
_claimRewards -> claimRewards -> Incentives.claimIncentives
_claimRewards -> claimRewards -> Incentives.claimIncentives -> BalancerHandler._finalize
_claimRewards -> claimRewards -> Incentives.claimIncentives -> BalancerHandler._finalize -> Used by many functions
_claimRewards -> claimRewards -> Incentives.claimIncentives -> BalancerHandler.claimIncentivesManual
_claimRewards -> claimRewards -> Incentives.claimIncentives -> BalancerHandler.claimIncentivesManual -> nTokenAction.nTokenClaimIncentives (External)
_claimRewards -> claimRewards -> Incentives.claimIncentives -> BalancerHandler.claimIncentivesManual -> nTokenAction.nTokenClaimIncentives
Many of the core functionalities of the protocol will be affected by the revert. Specifically, the BalancerHandler._finalize has the most impact as this function is called by almost every critical functionality of the protocol, including deposit, withdrawal, and liquidation. The worst-case scenario is that malicious users might exploit this trick to intentionally trigger a revert when someone attempts to liquidate their unhealthy accounts to block the liquidation, leaving the protocol with bad debts and potentially leading to insolvency if it accumulates.

## Recommendation
The current implementation uses a "push" approach where reward tokens are sent to the recipient during every update, which introduces additional attack surfaces that the attackers can exploit. Consider adopting a pull method for users to claim their rewards instead so that the transfer of reward tokens is disconnected from the updating of reward balances.
