# [M] `notifyLoss` can be frontrun by redeem

## Summary
Severity: Medium
Contest weight: 0.1214
Dataset id: 18407
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`notifyLoss` immediately transfer zchf from reserve to the minter, reducing the amount of reserve and hence the equity and zchf to claim per share.

While the deposit has 90 days cooldown before depositor can withdraw, current depositor that passed this cooldown can take advantage of a `notifyLoss` event by first frontrunning the `notifyLoss` by redeeming, then re-depositing into the protocol to take advantage of the reduced value per share.

`notifyLoss` can only be called by MintingHub::end, current depositor can bundle `redeem + end + deposit`, when they see a challenge that is ending in loss for the reserve.

## Recommendation
This is a re-current issue for most defi strategy to account loss in a mev-resistent way, a few possible solutions:

  1. create an additional window for MintingHub::end to be called by a whitelist, before it opens up to the public. The whitelist is trusted bot that will call `end` through private mempool.
  2. amortised the loss in the next coming period of time instead in 1 go with a `MAX_SPEED`.
  3. create an withdrawal queue such that the final withdrawal price is dependent on the upcoming equity change(s)
