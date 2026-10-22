# [M] Must reset approval before changing token approval, must do `approve(0)` first.

## Summary
Severity: Medium
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L67-L69
Type: audit-issue

## Details
# Must reset approval before changing token approval, must do `approve(0)` first.

## Summary

The "approve" function used in several smart contracts does not reset allowance to zero before setting a new allowance. This can potentially cause compatibility issues with tokens like USDT that require allowances to be reset to zero before assigning a new allowance.

## Vulnerability Detail

Some tokens (like USDT) do not work when changing the `allowance` from an existing non-zero allowance value. They must first be approved by zero (reset) and then the actual allowance must be approved.

## Impact

Some tokens (like USDT) do not function properly when changing the allowance from an existing non-zero value. They need to be first reset to zero before a new allowance can be set. Failing to do so can cause transactions to fail and disrupt the functionality of the smart contract when interacting with such tokens.

## Code Snippet

- [margin-dex/SwapRouter.vy#L67-L69](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L67-L69)
- [margin-dex/Vault.vy#L395](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L395)
- [spot-dex/Dca.vy#L204](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L204)
- [spot-dex/TrailingStopDex.vy#L174](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L174)

## Tool used

Manual Review

## Recommendation

The recommendation is to always reset the approval allowance to zero before setting a new value. This pattern is necessary for compatibility with all ERC20 tokens, including those that require the previous allowance to be zero before a new allowance can be set.

For example, in SwapRouter.vy:
```vy
    ERC20(_token_in).transferFrom(msg.sender, self, _amount_in)
    ERC20(_token_in).approve(UNISWAP_ROUTER, _amount_in)
```
It should be:

```vy
    ERC20(_token_in).transferFrom(msg.sender, self, _amount_in)
    ERC20(_token_in).approve(UNISWAP_ROUTER, 0)
    ERC20(_token_in).approve(UNISWAP_ROUTER, _amount_in)
```
This same pattern should be implemented in the other mentioned locations.
