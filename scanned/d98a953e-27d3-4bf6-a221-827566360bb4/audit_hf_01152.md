# [M] Malicious admin combing with low-level call can steal funds from user or form

## Summary
Severity: Medium
Reporter: ladboy233 - Sparkware
Contest weight: 0.5918
Dataset id: 4917
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The intended functionality of _dispatchTokens is to enable users to bridge tokens or conduct token swaps through the 1inch exchange, utilizing low-level calls (see LiquidityHandler.sol#L33):
```solidity
function _dispatchTokens(
    address bridge_,
    bytes memory txData_,
    address token_,
    uint256 amount_,
    uint256 nativeAmount_
)
    internal
    virtual
{
    if (bridge_ == address(0)) {
        revert Error.ZERO_ADDRESS();
    }
    if (token_ != NATIVE) {
        IERC20 token = IERC20(token_);
        token.safeIncreaseAllowance(bridge_, amount_);
    } else {
        if (nativeAmount_ < amount_) revert Error.INSUFFICIENT_NATIVE_AMOUNT();
    }
    (bool success,) = payable(bridge_).call{ value: nativeAmount_ }(txData_);
    if (!success) revert Error.FAILED_TO_EXECUTE_TXDATA(token_);
}
```
Address bridge is expected to be either Liﬁaddress or 1inch address. This function is usually called in this way:
```solidity
/// @dev dispatches tokens through the selected liquidity bridge to the destination contract
_dispatchTokens(
    superRegistry.getBridgeAddress(args_.liqRequest.bridgeId),
    args_.liqRequest.txData,
    args_.liqRequest.token,
    IBridgeValidator(bridgeValidator).decodeAmountIn(args_.liqRequest.txData, true),
    args_.liqRequest.nativeAmount
);
```
However, malicious admin can whitelist a malicious address so the query superRegistry.getBridgeAddress(args_.liqRequest.bridgeId) can return a token address. Consider the case:
1. A user grants infinite spending allowance to the router for UDSC token.
2. Admin is compromised and a hacker whitelists the USDC token address for bridge id 1000. So, superRegistry.getBridgeAddress(args_.liqRequest.bridgeId) returns the USDC address
3. The hacker craft the following payload data: abi.encodeWithSelector(IERC20.transferFrom.selector, address(victim), address(hacker), userUSDCBalance)
4. Then the hacker can steal the USDC that sits in users wallet by using the following low-level call: (bool success,) = payable(bridge_).call{ value: nativeAmount_ }(txData_);

## Recommendation
No data
