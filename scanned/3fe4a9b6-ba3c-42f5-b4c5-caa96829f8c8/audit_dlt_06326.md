# [M] Multiple Address ERC20 tokens could be drained from vaults containing them

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-24
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/29
Type: hats-finding

## Details
**Github username:** @PlamenTSV
**Twitter username:** @p_tsanev
**Submission hash (on-chain):** 0xbea277176ef2f1beca3d491a60194c9f264ce83aabdb88da8436c6fa59b13c5f
**Severity:** medium

**Description:**
**Description**\
The project specified all ERC20 and ERC777 tokens, except for fee-on-transfer and rebasing ones, to be usable as assets in any vaults.
That said, even though there are mitigations set to prevent exploiting arbitrary tokens that are not a vault's asset, tokens with multiple addresses(proxied tokens) are at risk at being stolen this way.


**Attack Scenario**\
The function at hand is ``calcLocalSwap()`` from the Volatile version of the vault. Unlike the Amplified version, this one has a specific check for if the weights of both provided tokens are equal and uses a uniswap-like calculation that does not involve the price curve.
This means that a user can pass any 2 arbitrary tokens and the check would pass, but in a regular scenario an attacker cannot drain any real value, apart from one he sends himself.
But if one of the tokens provided is an alternate address for a proxied token, that address' weight would too be 0, but it's balance would reflect the real balance of the token in the vault. Thus a malicious actor can:
1. Send any value of a random token he wants and pass it as token0
2. Pass a secondary address for the proxy token as token1, so both weights would be unregistered - 0
3. Entering the if-clause, weights do not play a part in calculating the amount out, thus the attacker can drain out any amount of token1 out of the vault.

**Attachments**

1. **Proof of Concept (PoC) File**

A verbal PoC would be like:
token0 is random, so the contract balance is A=0, weight is 0
token1 is the alternate address, so the balance is B, but the weight is 0
We enter the if-clause and using the formula:
``(B * amount) / (A + amount)`` we are able to drain the entire balance of B

Examples of the issue(containing similiar context to this repo):
https://solodit.xyz/issues/m-5-swaphandlersol-check-that-collateral-token-cannot-be-swapped-is-insufficient-for-tokens-with-multiple-addresses-sherlock-taurus-taurus-git

https://github.com/d-xo/weird-erc20?tab=readme-ov-file#multiple-token-addresses

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/29_
