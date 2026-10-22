# [H] 5.2.2 Wrong yield accumulation inclaimYieldAndEnter

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** Gate.sol#L

**Description:** TheclaimYieldAndEnterfunction does not accrue yield to theGatecontract itself (this) in case
xPYTwas specified. The idea is to accrue yield for the mint recipient first before increasing/reducing their balance
to not interfere with the yield rewards computation. However, in casexPYTis used, tokens are minted to theGate
before its yield is accrued.

Currently, the transfer fromthistoxPYTthrough thexPYT.depositcall accrues yield forthisafterthe tokens
have been minted to it (userPYTBalance * (updatedYieldPerToken - actualUserYieldPerToken) / PRECI-
SION) and its balance increased. This leads to it receiving a larger yield amount than it should have.

**Recommendation:** Accrue yield to the address receiving the minted tokens.

```
// accrue yield to recipient
// no need to do it if the recipient is msg.sender, since
// we already accrued yield in _claimYield
```
- if (pytRecipient != msg.sender) {
+ if (address(xPYT) != address(0) || pytRecipient != msg.sender)
    _accrueYield(
       vault,
       pyt,
- pytRecipient,
+ address(xPYT) == address(0)? pytRecipient : address(this),
    updatedPricePerVaultShare
    );
}

```
// mint NYTs and PYTs
yieldTokenTotalSupply[vault] += yieldAmount;
nyt.gateMint(nytRecipient, yieldAmount);
if (address(xPYT) == address(0)) {
// mint raw PYT to recipient
pyt.gateMint(pytRecipient, yieldAmount);
} else {
// mint PYT and wrap in xPYT
pyt.gateMint(address(this), yieldAmount);
if (pyt.allowance(address(this), address(xPYT)) < yieldAmount) {
// set PYT approval
pyt.approve(address(xPYT), type(uint256).max);
}
xPYT.deposit(yieldAmount, pytRecipient);
}
```
**Timeless:** Yes, if we usesweepbelow we can accrue yield in the same way as in_enter. Fix implemented in PR
#5.

**Spearbit:** Acknowledged.
