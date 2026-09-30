# [H] Missing slippage checks

## Summary
Severity: High
Contest weight: 0.2349
Dataset id: 684
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are no minimum amounts out, or checks that frontrunning/slippage is sufficiently mitigated. This means that anyone with enough capital can force arbitrarily large slippage by sandwiching transactions, close to 100%. See issue page for referenced code.

Recommend adding a minimum amount out parameter. The function reverts if the minimum amount isn’t obtained.

**[verifyfirst (Spartan) acknowledge:](https://github.com/code-423n4/2021-07-spartan-findings/issues/85#issuecomment-884593067)**

We acknowledge the issue for the protocol’s AMM, but if this becomes a large issue in the future, the router is easily upgradeable to include a minimum rate parameter.

Have changed this to confirmed; even though we already were aware of it; we have discussed and are happy to add in a UI-handed arg for minAmount now rather than reactively in the future. Disagree with severity though; this wasn’t a problem with V1 at all.

I’ll keep high risk as sandwich attacks are very common and risk of getting a bad swap is real.

## Recommendation
No recommendation
