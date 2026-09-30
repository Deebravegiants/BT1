# [M] User can sandwich pool writeOff and profit

## Summary
Severity: Medium
Contest weight: 0.2256
Dataset id: 20204
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A user can scan the mempool for pool writeoffs and profit by front-running and back-running it.
iFIL's value is based on the ratio of iFIL minted and InfinityPool#totalAssets.
Upon a user write-off, totalBorrowed is decreased, decreasing the pool's totalAssets (and therefore decreasing iFIL's price). A user can be monitoring the mempool and profit off of user write-offs.
Attack scenario
Let's consider there are only 2 equal stakers in InfinityPool. Both of them have 500 iFIL and totalAssets == 2000 (basically iFIL/wFIL ratio is 1:2) A borrower, whose principal was 200 wFIL, has been liquidated and will now be written off. (For simplicity of the example, let's consider no funds were recovered) 1 of the stakers can do the following to make a profit:
1. Scan the mempool for the write-off transaction.
2. When they see the transaction pending, they front-run it, selling all of their stake (leaving only 500 iFIL in circulation and 1000 wFIL in the pool)
3. The write-off transaction executes and it now lowers totalBorrowed by the borrower's principal. This also lowers the pool's totalAssets, making them 1000 - 200 = 800
4. The user can now deposit their 1000 wFIL back and they will be minted ((1000 / 800) * 500) = 625 iFIL
In the end, although the 2 users had equal stakes, the one who didn't take any action is left with 500 iFIL (equal to 800 wFIL) The user who did sandwich the transaction is left with 625 wFIL (equal to 1000 wFIL) The user who performed the sandwich attack not only didn't lose any money (unlike the other user), but will also now earn a bigger % of the fees from InfinityPool, although the initial investment of the 2 users was the same.
A user may profit off from innocent users by performing sandwich attacks.

## Recommendation
1 solution would be to lock deposits for a certain time. Another solution would be to set a fee on deposits/ withdrawals to make the attack unprofitable.
