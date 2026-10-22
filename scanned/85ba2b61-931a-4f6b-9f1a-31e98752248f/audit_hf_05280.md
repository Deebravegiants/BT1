# [H] Forwarder can be set to frozen address

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23514
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a forwarding‑to‑frozen‑address flaw in the dividend distribution logic. The contract’s setPayoutForwardAddress function does not verify whether the supplied forwarding address has been frozen, allowing a user or an attacker to designate a frozen holder as the recipient of forwarded payouts. When a dividend payout is executed, the system forwards the allocated amount to the designated address; if that address is frozen, the token transfer is silently dropped because frozen accounts are prohibited from receiving tokens. Consequently, both the original user’s payout balance and the frozen forwarder’s balance remain zero. If the user later removes the forwarding relationship while the forwarder is still frozen, the previously lost payout is not automatically re‑credited, leaving the user with no claimable tokens. This scenario can be reproduced by first minting tokens to a user and a separate forwarder, freezing the forwarder, setting the user’s payout forward address to the frozen forwarder, funding a payout, and observing that both balances stay at zero even after removing the forward. The root cause is the missing frozen‑address check and the absence of a fallback or reclamation path for payouts sent to frozen accounts. The impact is loss of dividend tokens for any holder that relies on forwarding, breaking the protocol’s accounting guarantees and potentially eroding user trust. The issue manifests whenever the protocol permits both freezing of holders and forwarding of payouts, and it is discovered through targeted audit tests that simulate the freeze‑then‑forward sequence. Because the contract does not revert or emit an error, the loss can be subtle and may only be noticed when users report missing balances. To remediate, the setPayoutForwardAddress function should revert if the target address is frozen, and the system should consider automatically cancelling or re‑routing existing forwards when an address becomes frozen, thereby preserving the intended accounting behavior and preventing token disappearance.

## Proof of Concept
```solidity
function test_freezeHolder_setPayoutForwardAddress_toFrozenForwarder() external {
address user1 = users[0];
address forwarder = users[1];
43
uint256 amountToMint = 1;
_whitelistAndMintTokensToUser(user1, amountToMint);
_whitelistAndMintTokensToUser(forwarder, amountToMint);
// freeze forwarder
remoraTokenProxy.freezeHolder(forwarder);
// forward user1 payouts to frozen address
remoraTokenProxy.setPayoutForwardAddress(user1, forwarder);
uint64 payoutDistributionAmount = 100e6;
_fundPayoutToPaymentSettler(payoutDistributionAmount);
// user1 must have 0 payout because it is forwarding to `forwarder`
uint256 user1PayoutBalance = remoraTokenProxy.payoutBalance(user1);
assertEq(user1PayoutBalance, 0);
// forwarder is frozen so receives no forwarded payout
uint256 forwarderPayoutBalance = remoraTokenProxy.payoutBalance(forwarder);
assertEq(forwarderPayoutBalance, 0);
// remove the forwarding while forwarder still frozen
remoraTokenProxy.removePayoutForwardAddress(user1);
// user1 can't claim any tokens - user1 has lost their payouts
user1PayoutBalance = remoraTokenProxy.payoutBalance(user1);
assertEq(user1PayoutBalance, 0);
}
```

## Recommendation
Recommended Mitigation: DividendManager::setPayoutForwardAddress should revert if forwardingAddress is frozen. When an address is frozen if that address has users forwarding to it, consider cancelling all those forwards.
