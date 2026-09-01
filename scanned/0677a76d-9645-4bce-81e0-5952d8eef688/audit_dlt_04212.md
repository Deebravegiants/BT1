# [M] _deposit() does not check the useless msg.value, which may cause the loss of funds

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/40
Type: sherlock-finding

## Details
bin2chen

medium

# _deposit() does not check the useless msg.value, which may cause the loss of funds

## Summary
DODORouteProxy#_deposit() 
When token != _ETH_ADDRESS_, msg.value is not used, but there is no detection of msg.value==0, so if it is transferred by mistake, the funds will be lost.

## Vulnerability Detail
need check msg.value==0 when not used
```solidity
    function _deposit(
        address from,
        address to,
        address token,
        uint256 amount,
        bool isETH
    ) internal {
        if (isETH) {
            if (amount > 0) {
                require(msg.value == amount, "ETH_VALUE_WRONG");
                IWETH(_WETH_).deposit{value: amount}();
                if (to != address(this)) SafeERC20.safeTransfer(IERC20(_WETH_), to, amount);
            }
        } else {
            //***@audit does not use msg.value, check ==0 if it is transferred by mistake ****/
            IDODOApproveProxy(_DODO_APPROVE_PROXY_).claimTokens(token, from, to, amount);
        }
    }
```

## Impact

if it is transferred by mistake, the funds will be lost.

## Code Snippet

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/40_
