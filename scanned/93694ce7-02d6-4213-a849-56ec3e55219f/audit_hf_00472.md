# [H] CoreCollection can be reinitialized

## Summary
Severity: High
Contest weight: 0.2254
Dataset id: 1905
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Reinitialization is possible for CoreCollection as `initialize` function sets `initialized` flag, but doesn’t control for it, so the function can be rerun multiple times.

Such types of issues tend to be critical as all core variables can be reset this way, for example `payableToken`, which provides a way to retrieve all the contract funds.

However, setting priority to be medium as `initialize` is `onlyOwner`. A run by an external attacker this way is prohibited, but the possibility of owner initiated reset either by mistake or with a malicious intent remains with the same range of system breaking consequences.

## Recommendation
Add `onlyUnInitialized` modifier to the `initialize` function:

This is a high severity issue and we intend to fix it. The mitigation step looks great and will be considered to fix the issue.

In my opinion, the severity level should be 3 (High Risk) instead of 2 (Med Risk)

Not convinced this is a high severity issue, since erroneously changing`payableToken` via a re-initialization can simply be corrected by a re-re-initialization to set it back correctly. Further, as the warden mentioned, the initialize function is behind `onlyOwner`.

However, if it can be shown that users other than the owner can end up losing value due to the owner abusing or erroneously using`initialize`, then it can be promoted to High Severity.

And just as I say that, #17 points that out clearly. So, yes, agreed, this is a High Severity issue.
