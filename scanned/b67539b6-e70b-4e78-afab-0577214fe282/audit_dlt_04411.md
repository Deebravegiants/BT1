# [M] approve(0) first

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-sentiment
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/12
Type: sherlock-finding

## Details
8olidity

medium

# approve(0) first

## Summary
Allowance was not set to zero first before changing the allowance.
## Vulnerability Detail
Some ERC20 tokens (like USDT) do not work when changing the allowance from an existing non-zero allowance value. For example Tether (USDT)'s `approve()` function will revert if the current approval is not zero, to protect against front-running changes of approvals.

The following attempt to call the `approve()` function without setting the allowance to zero first.
## Impact
A number of features within the vaults will not work if the approve function reverts.
## Code Snippet
https://github.com/sherlock-audit/2022-11-sentiment/blob/main/protocol-merged/src/core/AccountManager.sol#L276

```solidity
	// protocol-merged/src/core/AccountManager.sol
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
        account.safeApprove(token, spender, amt);
    }
```
## Tool used

Manual Review


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/12_
