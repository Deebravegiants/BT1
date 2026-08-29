# [M] Prevent Victim User From gaining portalEnergyEarned

## Summary
Severity: Medium
Chain: Smart contract
Component: Possum-Labs--Portals-
Published: 2023-11-18
Source: https://github.com/hats-finance/Possum-Labs--Portals--0xed8965d49b8aeca763447d56e6da7f4e0506b2d3/issues/47
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x11b61e6b0f2f96d92a62b21637a4f55a22e181795e4fc231a7633caaaf901b5a
**Severity:** medium

**Description:**
**Description**\
In the _updateAccount function, the calculation of portalEnergyEarned is susceptible to manipulation by malicious users if their staked balance is less than SECONDS_PER_YEAR. By repeatedly calling burnPortalEnergyToken with a small amount(amount 1) and the victim user as _recipient, a malicious user could prevent victim users from earning portalEnergyEarned.

**Impact**\
While the impact is currently limited to users with low staking balances, it could have a more significant impact if the protocol decides to use low decimal tokens as principal tokens.


1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->
for example, user A has 31535999 staked amount.
maliouse user could call burnPortalEnergyToken(1, UserA) every seconds.
so 31535999 * 1 / 31536000=0 and user A doesn't get any energy.

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
It's recommended to remove the unnecessary account update in the burnPortalEnergyToken function to prevent the manipulation of portalEnergyEarned. The update seems unnecessary for the context of burning portal energy tokens, and removing it mitigates the vulnerability.

```diff
         /// @dev Require that the caller has sufficient tokens to burn
         if(portalEnergyToken.balanceOf(address(msg.sender)) < _amount) {revert InsufficientBalance();}
 
-        ///@dev Update the recipient´s stake data
-        _updateAccount(_recipient,0);
-
         /// @dev Increase the portalEnergy of the recipient by the amount of portalEnergyToken burned
         accounts[_recipient].portalEnergy += _amount;
```
