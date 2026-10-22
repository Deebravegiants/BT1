# [C] C-01 | Inﬂation Exploit

## Summary
Severity: Critical
Contest weight: 0.3732
Dataset id: 2246
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the LeveragedToken contract has no existing supply (right after its deployment) a new minter operates on an initial exchange rate of 1 for the ﬁrst deposit. Under normal conditions, once tokens are minted, a user must call redeemFor to withdraw margin. However, the contract also provides a raw burn function that simply destroys the user’s leveraged tokens without adjusting or withdrawing margin from the underlying Synthetix position. A malicious ﬁrst minter can exploit this by:
• Minting a large amount: Suppose the user deposits 100000 sUSD into a brand-new LeveragedToken. He receives 100000 leveraged tokens (exchange rate = 1).
• Burning all the leveraged tokens except one: The user calls burn(leverageTokenBalance - 1). This reduces the totalSupply drastically (e.g., from 100000 down to 1), but the contract margin remains the same (it does not call _withdrawMargin).
• As a result, exchangeRate inﬂates sharply (totalValue remains 100000, but totalSupply is only 1).
• This single remaining token now has a massively increased claim on the LeveragedToken’s margin.
• If a new user attempts to mint with an amount lower than the malicious user’s original deposit (e.g., just 10000 sUSD), the exchange rate calculates the new minted tokens at the already‐inﬂated ratio. The ﬁrst minter’s single token “absorbs” the new deposit, growing their share of the margin.
• The new minter performs the sUSD deposit but does not receive any leveraged token (totalSupply remains 1). This leads to a scenario where the malicious user can redeem their one leveraged token later for a higher amount than the original 100000 sUSD at the expense of other depositors.
• In a situation where future users set slippage, their deposits will always revert if its lower than the initial 100000 sUSD as, due to rounding, they would receive 0 leveraged tokens in exchange for their sUSD.

## Proof of Concept
https://gist.github.com/r0bert-ethack/037b8285a93757e810659b363dce21b5

## Recommendation
Consider removing the public burn function from the LeveragedToken contract.
