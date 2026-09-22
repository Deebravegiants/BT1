# [C] 5.1.1 MintPerpetualYieldTokensfor free by self-transfer

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk

**Context:** PerpetualYieldToken.sol#L

**Description:** ThePYT.transferandtransferFromfunctions operate on cached balance values. When transfer-
ring tokens to oneself the decreased balance is overwritten by an increased balance which makes it possible to
mint PYT tokens for free.

Consider the following exploit scenario:

- AttackerAself-transfers by callingtoken.transfer(A, token.balanceOf(A)).
- balanceOf[msg.sender]is first set to zero but then overwritten bybalanceOf[to] = toBalance + amount,
    doublingA’s balance.

**Recommendation:** Fix the issue intransferandtransferFromby operating on the latest storage balances
instead of cached values.

**Timeless:** Would checking for self-transfers and doing an early return be the best way to solve it?

**Spearbit:** It would be best regarding gas efficiency nevertheless it should still trigger a
gate.beforePerpetualYieldTokenTransfer call once to accrue the yield because the user would
expect any transfer to accrue yields forfromandto, and maybe someone is reliant on this. Additionally, it should
also trigger theTransferevent for ERC20 compliance.

**Timeless:** Not sure about triggeringgate.beforePerpetualYieldTokenTransferduring self transfers, seems like
a niche use case.

**Spearbit:** Then its behavior is inconsistent. Because self-transfers are a niche use case anyway, might as well do
the additional call to make it consistent. It would not increase gas cost per execution for non-self-transfer calls as
you need theifbranch + return anyway.

**Timeless:** Implemented in PR #4.

**Spearbit:** The bug still exists intransferFromdiff PR #4.

You’re checkingmsg.sender != tobut it should befrom != toin this case - you always want to check the balance
owners. The test should be with aspenderdifferent fromfromand all three parties aretester.

**Timeless:** Nice catch, fixed in this commit.

**Spearbit:** Acknowledged.
