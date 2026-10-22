# [H] processWithdrawalQueue can permanently fail

## Summary
Severity: High
Contest weight: 0.6155
Dataset id: 19708
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Withdrawals are made in a two-step process. First, a user starts the withdrawal,
and if the initial validation succeeds, the withdrawal is added to queuedWithdrawals.
After a withdrawal delay, a user can call processWithdrawalQueue(). This function
does not allow a user to process the withdrawal based on an id but processes
withdrawals in chronological order. When a user wants to withdraw funds, all other
withdrawals that were initiated before need to be processed first. This can be
problematic if one of the withdrawals fails for an unforeseen reason because then,
the withdrawal queue is stuck, and no other withdrawals after the failing one can
take place. Such a scenario could occur when a user with LP tokens gets
blacklisted and initiates a withdrawal. USDC is planned to be the quote asset, and
it has a blacklist function that has been used in the past for various reasons.
_transferQuote() is called when a withdrawal is processed as part of
processWithdrawalQueue(). It attempts a token transfer and expects it to succeed in
line 1060. It has no mechanism to handle a failing transfer and skip the queue.
The withdrawal queue could become permanently stuck, and users will not be able
to withdraw their funds anymore from the LiquidityPool contract.
sol#L428
```solidity
function _transferQuote(address to, uint amount) internal {
    amount = ConvertDecimals.convertFrom18(amount, quoteAsset.decimals());
    if (amount > 0) {
        if (!quoteAsset.transfer(to, amount)) {
            revert QuoteTransferFailed(address(this), address(this), to, amount);
        }
    }
}
```
sol#L1057-L1064

## Recommendation
The transfer call should be wrapped into a try/catch statement. If the transfer call
in processWithdrawalQueue() fails, then the withdrawal should be skipped.
