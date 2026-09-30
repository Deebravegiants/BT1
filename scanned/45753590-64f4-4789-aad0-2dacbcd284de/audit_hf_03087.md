# [M] Failing withdrawals could permanently freeze the queue

## Summary
Severity: Medium
Contest weight: 0.2009
Dataset id: 17452
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Withdrawals are done in a two-step process. First, a user starts the withdrawal and if
the initial validation succeeds, the withdrawal is added to queuedWithdrawals. After a
withdrawal delay, a user can then call processWithdrawalQueue. This function does
not allow a user to process the withdrawal based on an id but processes withdrawals
in chronological order. So if a user wants to withdraw funds, all other withdrawals that
were initiated before need to be processed first. This can be problematic if one of the
withdrawals fails for an unforeseen reason because then, the withdrawal queue is
stuck and no other withdrawals after the failing one can take place.
Deposits have the same two-step process and the design of the queue could lead to a
similar issue where a processing failure for a deposit could freeze the deposit queue.
The withdrawal queue returns without processing the withdrawal if
totalTokensBurnable is 0. The withdrawal can not be processed until the condition
changes. There could be other undiscovered issues that might cause failures or
reverts, in which case the withdrawal queue could become stuck as well.
The withdrawal queue could become permanently stuck and users will not be able to
withdraw their funds anymore from the LiquidityPool contract. This will cause a DoS.

## Recommendation
It is recommended to change the design of the deposit and withdrawal process so that
funds can be processed without a queue. Users should be able to process their
deposits or withdrawals regardless of a specific order.
A queue is necessary due to the potential of the pool filling up blocking withdrawals. In
those scenarios, those who came first should be able to withdraw their funds first.
We've endeavoured to make sure that the queue processing is as robust as possible.
In the case of some failings in circuit breakers etc. the guardian has the ability to
process the queue.
Sounds reasonable.
