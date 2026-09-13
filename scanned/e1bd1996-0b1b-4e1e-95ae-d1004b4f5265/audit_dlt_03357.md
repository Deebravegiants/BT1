# [M] fee-on-transfer underlying can cause problems

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-09-swivel
Published: 2021-10-06
Source: https://github.com/code-423n4/2021-09-swivel-findings/issues/156
Type: code-finding

## Details
# Handle

0xsanson


# Vulnerability details

## Impact
The current implementation doesn't work with fee-on-transfer underlying tokens. Considering that Compound can have these kind of tokens (ex. USDT can activate fees), this issue can affect the protocol.

The problem arise when transferring tokens, basically blocking all functions in Swivel.sol for that particular token, since the contract wrongly assumes balances values.
This becomes particularly problematic in the following scenario: a market for USDT is running without problems, then they activate the fee: this effectively blocks users from redeeming the underlying.

## Proof of Concept
`grep 'transfer' Swivel.sol` for a complete list of affected lines (basically every `tranfer` or `transferFrom` of underlying tokens). Also `grep 'redeemUnderlying' Swivel.sol`.

For example:
```js
require(CErc20(mPlace.cTokenAddress(u, m)).redeemUnderlying(redeemed) == 0, 'compound redemption failed');
// transfer underlying back to msg.sender
Erc20(u).transfer(msg.sender, redeemed);
```
This would fail (revert) since the contract would have received less than `redeemed` tokens.

## Tools Used
editor

## Recommended Mitigation Steps
If the protocol wants to use all possible Compund's tokens, a way to handle these tokens must be implemented. A possible way to do it is to check the balance of the contract before and after every time a token is transferred to see the effective quantity. To help keeping the code clear, a function like [Compund's `doTransferIn`](https://github.com/compound-finance/compound-protocol/blob/master/contracts/CErc20.sol#L156) can be implemented.
