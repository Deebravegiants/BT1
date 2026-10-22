# [M] No deadline parameter in `sellAllAmount`

## Summary
Severity: Medium
Contest weight: 0.3127
Dataset id: 18459
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of the absence of a deadline parameter in the sellAllAmount functions of the automated market maker contract. Because the function does not record an expiration time, a transaction that is signed and broadcast can remain in the mempool indefinitely if the attached gas fee is too low or network congestion is high. When the transaction finally becomes attractive to miners, the market price of the traded assets may have moved substantially. The contract only checks that the output amount is above a user‑provided minOutputAmount, which was calculated at the time of signing. Consequently, the transaction can be executed at a price that is far worse for the user, resulting in a trade that yields far less value than expected, or in the worst case, a loss caused by a front‑running or sandwich attack performed by a MEV bot that exploits the outdated slippage tolerance. The impact is that users may receive far fewer tokens than anticipated, see their balances shrink unexpectedly, or experience a trade that appears to have been executed at an unfair rate. The issue manifests whenever a transaction is pending for an extended period, which can happen on L2 networks with variable gas pricing, during airdrop spikes, or when users deliberately set low fees. All participants who rely on the AMM – individual traders, liquidity providers, and the protocol itself – are affected because the economic guarantees of the swap are broken. The problem was identified during a formal audit that examined the function signatures and noticed the missing deadline field, a common safeguard in AMM designs to prevent delayed execution. It is difficult to notice in normal operation because the function succeeds and returns a valid amount; the loss only becomes apparent after the price shift, which may be attributed to market volatility rather than a contract flaw. The recommended remediation is to introduce a deadline argument that is compared against the block timestamp at execution, rejecting any transaction whose deadline has passed, thereby restoring the intended time‑sensitivity of the trade and preventing malicious re‑ordering or unintended slippage. This class of bug is a time‑bound execution flaw, where the lack of an expiration check allows pending transactions to be replayed under changed market conditions, violating the business logic that a trade should be executed at roughly the price expected at signing time.

## Proof of Concept
Consider following scenario:

1. Alice wants to create order of 1000DAI for 1 ETH. She signs the transaction with `minOutputAmount = 0.99 ETH` to allow for some slippage.
2. The transaction is submitted to the mempool; however, Alice chose a transaction fee that is too low for miners to be interested in including her transaction in a block. The transaction stays pending in the mempool for extended periods, which could be hours, days, weeks, or even longer.
3. The average gas fee dropped far enough for Alice’s transaction to become interesting again for miners to include it. In the meantime, the price of ETH could have drastically changed. She will still at least get 0.99 ETH due to `minOutputAmount`, but the DAI value of that output might be significantly lower. She has unknowingly performed a bad trade due to the pending transaction she forgot about.

An even worse way this issue can be maliciously exploited is through MEV:

1. The swap transaction is still pending in the mempool. Average fees are still too high for miners to be interested in it. The price of `___` has gone up significantly since the transaction was signed (lets say its not dai now and some other token), meaning Alice would receive a lot more ETH when the swap is executed. But that also means that her `minOutputAmount` value is outdated and would allow for significant slippage.
2. A MEV bot detects the pending transaction. Since the outdated `minOutputAmount` now allows for high slippage, the bot sandwiches Alice, resulting in significant profit for the bot and significant loss for Alice.

## Recommendation
Add deadline param

In my opinion, this is a good recommendation but is OOS.  
Due to MEV argument - seems network-level to me - nice enhancement idea though.

Ignoring the MEV argument since we’re dealing with L2s.

I think the first portion has some merit. Reference [here](https://code4rena.com/reports/2022-06-canto-v2/#m-01-stableswap---deadline-do-not-work).

Because front-running is a key aspect of AMM design, deadline is a useful tool to ensure that your tx cannot be “saved for later”.

While both Arbitrum & Optimism has minimum gas prices, network congestion could mean that the tx doesn’t get mined until they go back down (eg. trading during Arb airdrop).

It’s again a user-conditional error, which, following the reasoning in [#1298](https://github.com/code-423n4/2023-04-rubicon-findings/issues/1298), would be medium severity.
