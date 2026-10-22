# [M] Funds can be stolen from the FixedStrikeOptionTeller

## Summary
Severity: Medium
Contest weight: 0.4580
Dataset id: 20196
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
without providing the necessary collateral. A malicious receiver can exploit this to mint put options for free. Anyone can create (issue) put option tokens with the create function in the contract. The issue occurs if the result of the multiplication in line 283, amount * strikePrice is smaller than 10**payoutTokendecimals, where decimals is the number of decimals of the payout token. For example, assume the following scenario:
() Parameter Description ()
Quote token $USDC. 6 decimals
Payout token $GMX. 18 decimals
payoutTokendecimals 18 decimals
amount 1e10. Amount (amount_) supplied to the create function, in payout token decimals
strikePrice 50e6 ~ 50 USD. The strike price of the option token, in quote tokens.
()
oken.
(1e10 * 50e6) / 10**18 = 5e17 / 10**18 = 0.5 → rounded down to 0 due to integer division.
As observed, the result is rounded down to zero due to the numerator being smaller than the denominator. This results in 0 quote tokens to be transferred from the caller to the contract, and in return, the caller receives 1e10 (amount) option tokens. This process can be repeated to mint an arbitrary amount of option tokens for free. Put options can be minted for free without providing the required quoteToken collateral. This is intensified by the fact that a malicious receiver, which anyone can be, can exploit this issue by deploying a new option token (optionally with a very short expiry), repeatedly minting free put options to accumulate option tokens, and then, once the option expires, call reclaim to receive quote token collateral. This collateral, however, was supplied by other users who issued (created) option tokens with the same quote token. Thus, the malicious receiver can drain funds from other users and cause undercollateralization of those affected option tokens.
```solidity
236: function create(
237:     uint256 amount_
238: ) external override nonReentrant {
...
// [...]
268:
269:     // Transfer in collateral
270:     // If call option, transfer in payout tokens equivalent to the amount of option tokens being issued
271:     // If put option, transfer in quote tokens equivalent to the amount of option tokens being issued * strike price
272:     if (call) {
...
// [...]
281:     } else {
282:         // Calculate amount of quote tokens required to mint
283:         uint256 requiredCollateral = (amount_ * strikePrice) / 10 ** payoutToken.decimals();
284:
285:         // Transfer quote tokens from user
286:         // Check that amount received is not less than amount expected
287:         // Handles edge cases like fee-on-transfer tokens (which are not supported)
288:         uint256 startBalance = quoteToken.balanceOf(address(this));
289:         quoteToken.safeTransferFrom(msg.sender, address(this), requiredCollateral);
290:         uint256 endBalance = quoteToken.balanceOf(address(this));
291:         if (endBalance - startBalance < requiredCollateral) revert Teller_UnsupportedToken(address(quoteToken));
292:     }
293:
294:     // Mint new option tokens to sender
295:     optionToken.mint(msg.sender, amount_);
296: }
```

## Recommendation
No recommendation available
