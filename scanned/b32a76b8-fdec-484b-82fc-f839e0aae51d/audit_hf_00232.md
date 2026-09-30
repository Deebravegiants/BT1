# [M] MixinRefunds: frontrun updateKeyPricing

## Summary
Severity: Medium
Contest weight: 0.1679
Dataset id: 1195
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability lies in the way refunds are calculated in the lock contract’s MixinRefunds module. When a lock manager changes the global keyPrice for a lock, the refund function continues to use the current keyPrice rather than the price that was actually paid for each individual key. Because the contract does not keep a record of the original purchase amount for each key and does not enforce a cancellation penalty automatically, an attacker can exploit this mismatch. The attack scenario is as follows: an attacker monitors the blockchain for a pending transaction that will call updateKeyPricing() to raise the key price. The attacker front‑runs that transaction, purchasing a large number of keys at the lower, pre‑change price. After the price has been raised, the attacker invokes the refund function for the keys they just bought. The refund calculation now uses the higher, updated keyPrice, causing the contract to return more ether than was originally paid. As a result, the attacker can withdraw the excess value, effectively draining funds that were supposed to belong to the lock owner. This issue manifests only when the lock price is increased without an accompanying penalty and when the refund logic is invoked after the price change. It affects any user who can submit a refund request, the lock manager who loses revenue, and the overall protocol integrity because the accounting assumptions—that refunds should never exceed the amount originally paid—are violated. The flaw was discovered during a security audit that examined the interaction between updateKeyPricing() and the refund pathway; it can be difficult to spot because refunds work correctly under stable pricing, and the discrepancy appears only in the narrow window after a price change. To remediate the issue, the contract should record the purchase price for each key at the time of sale and use that stored value when processing refunds. Additionally, the lock manager should apply a cancellation penalty that reflects the price difference before adjusting the keyPrice, or the protocol should enforce penalty logic on‑chain to prevent refunds from being calculated at the new price. By aligning the refund amount with the actual amount paid, the protocol restores its financial guarantees and prevents malicious front‑running withdrawals.

## Proof of Concept
When `updateKeyPricing()` is called to increase the price of a key, it is possible to frontrun this call and buy many keys at the cheaper price then request for a refund at the higher price.

## Recommendation
Keep track of the price at which keys are purchased so that when you issue a refund, you use the original keyPrice to refund instead of the updated keyPrice

This is only true for locks where there is no penalty. We should make it clear on the front-end that when changing the price it is recommended to set up a penalty (at least temporarily) for the price difference so that no key can be refunded for the full price.

Circling back on this, I’m not sure how a penalty would be correctly applied to all locks. Wouldn’t users who wanted to get a refund for their key get penalised if they purchase after the change in key price? I think it would also be safer to update the key price and apply the penalty in the one transaction.

I think that is a good finding, but there again (like often) I think this is pretty edgy. The cancellation penalty is pretty easy to apply just to a single lock from the [lock manager’s perspective](https://github.com/unlock-protocol/unlock/blob/b7c5a555efc3c2be619cbb942eb67d4008baa049/smart-contracts/contracts/mixins/MixinRefunds.sol#L70). Before changing the lock price, a lock manager can easily apply a penalty for the difference in price. IE if I change the price from 10 to 12, I apply a penalty for 2 and anyone who tries to abuse this will only get a refund of 12-2 = 10.
 
On top of that we’re actually storing the amount paid for the latest key as part of our next upgrade to support automatically recurring memberships, which should make things even more robust as anyone will only get re-imbursed based on what they paid…

Considering the sponsor’s comments and after some further discussion on Discord. I think it is more correct to downgrade this to `medium` severity. While it isn’t clear, the lock manager is expected to apply a penalty before updating the cost of a membership such that users cannot game the price difference. However, this isn’t enforced on-chain or documented anywhere so based on the judge’s and warden’s context at the time, this seemed like a valid `high` severity issue. It is important to note that users who refund their membership after purchasing a membership post price change will be refunded less than users who purchased their memberships before the price change. The sponsor is looking to integrate these fixes in their next upgrade.
