# [M] Staker can pay off interest of delinquent debtor and back claim reward tokens for the entire time the loan was delinquent

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/116
Type: sherlock-finding

## Details
TurnipBoy

medium

# Staker can pay off interest of delinquent debtor and back claim reward tokens for the entire time the loan was delinquent

## Summary

Reward tokens are not distributed to stakers for the portion of their stake that it held by delinquent loans. A staker can pay off the debt of a delinquent loan to bring it current and claim reward tokens for the full amount as if the debt had never been delinquent. 

## Vulnerability Detail

    function _getUserInfo(
        IUserManager userManager,
        address account,
        address token,
        uint256 futureBlocks
    )
        internal
        returns (
            UserManagerAccountState memory,
            Info memory,
            uint256
        )
    {
        Info memory userInfo = users[account][token];
        uint256 lastUpdatedBlock = userInfo.updatedBlock;
        if (block.number < lastUpdatedBlock) {
            lastUpdatedBlock = block.number;
        }

        uint256 pastBlocks = block.number - lastUpdatedBlock + futureBlocks;

        UserManagerAccountState memory userManagerAccountState;
        (userManagerAccountState.totalFrozen, userManagerAccountState.pastBlocksFrozenCoinAge) = userManager
            .updateFrozenInfo(account, pastBlocks);

        return (userManagerAccountState, userInfo, pastBlocks);

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/116_
