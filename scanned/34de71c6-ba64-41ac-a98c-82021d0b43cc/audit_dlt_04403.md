# [M] `safeApprove` doesn't support for Approval Race Protections

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-sentiment
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/24
Type: sherlock-finding

## Details
Tomo

medium

# `safeApprove` doesn't support for Approval Race Protections

## Summary
`safeApprove` doesn't support some ERC20 tokens that have approval race protections.

## Vulnerability Detail
Some tokens (like USDT) do not work when changing the allowance from an existing non-zero allowance value.

They must first be approved by zero and then the actual allowance must be approved.

https://github.com/d-xo/weird-erc20#approval-race-protections

This is to protect from an ERC20 front-run attack vector described here.
https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.b32yfk54vyg9

## Impact
USDT contains one of these ERC20 tokens.
Therefore, users can't approve USDT in this protocol.

## Code Snippet
https://github.com/sherlock-audit/2022-11-sentiment/blob/main/protocol-merged/src/core/AccountManager.sol#L264-L277
``` solidity
    function approve(
        address account,
        address token,
        address spender,
        uint amt
    )
        external
        nonReentrant
        onlyOwner(account)
    {
        if(address(controller.controllerFor(spender)) == address(0))
            revert Errors.FunctionCallRestricted();
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/24_
