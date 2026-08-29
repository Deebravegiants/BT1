# [M] Lack of protection when caling `CusdcV3Wrapper._withdraw`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-02
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/8
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/compoundv3/CusdcV3Wrapper.sol#L127-L170


# Vulnerability details

## Impact
When unwrapping the `wComet` to its rebasing `comet`, users with an equivalent amount of `wComet` invoking `CusdcV3Wrapper._withdraw` at around the same time could end up having different percentage gains because `comet` is not linearly rebasing.

Moreover, the rate-determining `getUpdatedSupplyIndicies()` is an internal view function inaccessible to the users unless they take the trouble creating a contract to inherit CusdcV3Wrapper.sol. So most users making partial withdrawals will have no clue whether or not this is the best time to unwrap. This is because the public view function [underlyingBalanceOf](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/compoundv3/CusdcV3Wrapper.sol#L225-L231) is only directly informational when `amount` has been entered as `type(uint256).max`. 

## Proof of Concept
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/compoundv3/CusdcV3Wrapper.sol#L134-L170

```solidity
    function _withdraw(
        address operator,
        address src,
        address dst,
        uint256 amount
    ) internal {
        if (!hasPermission(src, operator)) revert Unauthorized();
        // {Comet}
        uint256 srcBalUnderlying = underlyingBalanceOf(src);
        if (srcBalUnderlying < amount) amount = srcBalUnderlying;
        if (amount == 0) revert BadAmount();

        underlyingComet.accrueAccount(address(this));
        underlyingComet.accrueAccount(src);

        uint256 srcBalPre = balanceOf(src);
        CometInterface.UserBasic memory wrappedBasic = underlyingComet.userBasic(address(this));
        int104 wrapperPrePrinc = wrappedBasic.principal;

        // conservative rounding in favor of the wrapper
        IERC20(address(underlyingComet)).safeTransfer(dst, (amount / 10) * 10);

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-reserve-findings/issues/8_
