# [H] 5.2.24WithdrawProxyallows redemptions beforePublicVaultcallstransferWithdrawReserve.

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** WithdrawProxy.sol#L172-L175
**Description:** Anytime there is a withdraw pending (i.e. someone holdsWithdrawProxyshares), shares may be
redeemed so long astotalAssets() > 0ands.finalAuctionEnd == 0.
Under normal operating conditionstotalAssets()becomes greater than 0 when thenPublicVaultcallstrans-
ferWithdrawReserve.
totalAssets()can also be increased to a non zero value by anyone transferring WETH to the contract.
If this occurs and a user attempts to redeem, they will receive a smaller share than they are owed.
Exploit scenario:

- Depositorredeems fromPublicVaultand receivesWithdrawProxyshares.
- Malicious actor deposits a small amount of WETH into theWithdrawProxy.
- Depositor accidentallyredeems, or is tricked intoredeeming, from theWithdrawProxywhiletotalAssets()
    is smaller than it should be.
- PublicVaultproperly processes epoch and fullwithdrawReserveis sent toWithdrawProxy.
- All remaining holders ofWithdrawProxyshares receive an outsized share as the previous shares were-
    deemed for the incorrect value.
**Recommendation:**
- Option 1:
Consider being explicit in opening the WithdrawProxy for redemptions (redeem/withdraw) by requiring
s.withdrawReserveReceivedto be a non zero value:
- if (s.finalAuctionEnd != 0) {
+ if (s.finalAuctionEnd != 0 || s.withdrawReserveReceived == 0) {
// if finalAuctionEnd is 0, no auctions were added
revert InvalidState(InvalidStates.NOT_CLAIMED);
}

Astaria notes there is a second scenario where funds are sent to theWithdrawProxy: auction payouts. For the
above recommendation to be complete, auction payouts or claiming MUST also setwithdrawReserveReceived.

- Option 2:
Instead of inferring when it is safe to withdraw based onfinalAuctionEndandwithdrawReserveReceived, con-
sider explicitly marking the withdraws asopenwhen it is both safe to withdraw (i.e. expected funds deposited) and
the vault has claimed its share.
