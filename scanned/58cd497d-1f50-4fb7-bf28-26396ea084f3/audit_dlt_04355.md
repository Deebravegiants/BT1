# [M] When debt becomes overdue the staker is penalized for the entire time since last payment rather than just the time the debt is overdue

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/136
Type: sherlock-finding

## Details
TurnipBoy

medium

# When debt becomes overdue the staker is penalized for the entire time since last payment rather than just the time the debt is overdue

## Summary

Stakers are given a reduced reward payout for debt lent out that is now overdue. This penalty should apply after the debt has gone overdue, however when it is calculated it penalizes the staker for entire period since the last payment.

## Vulnerability Detail

    for (uint256 i = 0; i < voucheesLength; i++) {
        Vouchee memory vouchee = vouchees[staker][i];

        Vouch memory vouch = vouchers[vouchee.borrower][vouchee.voucherIndex];

        uint256 lastUpdated = vouch.lastUpdated;
        uint256 diff = block.number - lastUpdated;

        if (overdueBlocks < diff) {
            uint96 locked = vouch.locked;
            memberTotalFrozen += locked;

            if (pastBlocks >= diff) {
                memberFrozenCoinAge += (locked * diff);
            } else {
                memberFrozenCoinAge += (locked * pastBlocks);
            }
        }
    }

The lines above are used to determine the amount of penalty to apply for stakers lending out to delinquent debt. If `pastBlocks >= diff` then the user will be penalized for `(locked * diff)` in this case `diff = block.number - lastUpdated`. The result is that the staker is charged a penalty since that last payment rather than the amount of time that the debt is overdue. In the scenario where a borrower is only 1 day overdue, the staker will be charged a penalty for all 31 days since they made their last payment, which is unfair to the staker.

A secondary issue with this is that if a staker withdraws their rewards days before a borrower goes delinquent, the sudden backcharge of reward penalties could cause a revert in `Comptroller.sol#_calculateRewards`:

        if (userStaked * pastBlocks < frozenCoinAge) revert FrozenCoinAge();


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/136_
