# [M] Deflationary tokens are not supported

## Summary
Severity: Medium
Contest weight: 0.1784
Dataset id: 577
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are ERC20 tokens that may make certain customizations to their ERC20 contracts. One type of these tokens is deflationary tokens that charge a certain fee for every `transfer()` or `transferFrom()`.

The `deposit()` functions of `Insurance` and `TracerPerpetualSwaps` assume that the external ERC20 balance of the contract increases by the same amount as the `amount` parameter of the `transferFrom`.

The user is credited the full amount without the taxes (`userBalance.position.quote`).

Recommend as one possible mitigation, measuring the asset change right before and after the asset-transferring functions.

Most likely not a medium risk as you can do a lot more nasty things than just use rebasing tokens. Since the owner of a market can set their own quote token, this token could be a token they control the supply of allowing them to arbitrarily transfer tokens between accounts, etc.

As such, this sort of falls outside of our trust model. Market creators should use tokens that behave as “standard” ERC20s. We will make a not that rebasing and deflationary tokens should not be used as quote tokens without weird behaviour.

Would be better as a low or informational issue due to this.

Marking this as low risk as it seems to fall outside of the trust model, yet important enough to communicate to users explicitly.

## Recommendation
No recommendation
