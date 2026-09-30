# [M] ICE-2 | Uncapped Minting

## Summary
Severity: Medium
Contest weight: 0.0296
Dataset id: 9029
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an uncapped minting flaw that allows the contract owner to increase the token totalSupply beyond the declared maxSupply by invoking the reserveForGiveaway function with an arbitrarily large amount. The root cause is the absence of a validation check that compares the amount to be minted with the remaining supply capacity; the function does not enforce the invariant that totalSupply must never exceed maxSupply. An attacker who controls the owner role can exploit this by calling reserveForGiveaway and specifying a huge token amount, causing the internal accounting to record a totalSupply that is larger than the intended cap. This inflationary minting breaks the economic assumptions of the token, dilutes existing holders, and can lead to loss of confidence, price depreciation, or protocol instability. The issue manifests whenever the owner executes reserveForGiveaway without a safeguard, which may be rare in normal operation but can be triggered at any time because the function is publicly callable by the owner. All token holders, users of the platform, and any downstream contracts that rely on the maxSupply invariant are affected, as they may receive fewer relative shares of the token pool or see unexpected supply spikes. The flaw was identified during a manual security audit that reviewed the token’s minting pathways and noticed that the reserveForGiveaway routine lacked a require statement limiting the mint amount. Because the function is restricted to the owner, the problem can be subtle and may not surface in routine testing unless the owner’s privileges are exercised with extreme values. To remediate, the contract should include a check such as require(totalSupply + amount <= maxSupply) (or an equivalent conditional) before performing the mint, thereby preserving the maxSupply constraint and preventing arbitrary inflation. Conceptually, this belongs to the class of “unbounded minting” or “supply cap bypass” bugs, where privileged mint functions fail to enforce a hard cap, leading to potential token supply overflow and economic distortion.

## Recommendation
Add a require or an if statement to make sure the amount of tokens to reserve plus the current supply does not exceed the max supply.
