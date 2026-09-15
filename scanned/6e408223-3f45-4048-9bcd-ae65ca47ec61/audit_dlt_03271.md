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

        wrappedBasic = underlyingComet.userBasic(address(this));
        int104 wrapperPostPrinc = wrappedBasic.principal;

        // safe to cast because principal can't go negative, wrapper is not borrowing
        uint256 burnAmt = uint256(uint104(wrapperPrePrinc - wrapperPostPrinc));
        // occasionally comet will withdraw 1-10 wei more than we asked for.
        // this is ok because 9 times out of 10 we are rounding in favor of the wrapper.
        // safe because we have already capped the comet withdraw amount to src underlying bal.
        // untested:
        //      difficult to trigger, depends on comet rules regarding rounding
        if (srcBalPre <= burnAmt) burnAmt = srcBalPre;

        accrueAccountRewards(src);
        _burn(src, safe104(burnAmt));
    }
```
As can be seen in the code block of function `_withdraw` above, `underlyingBalanceOf(src)` is first invoked.

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/compoundv3/CusdcV3Wrapper.sol#L225-L231

```solidity
    function underlyingBalanceOf(address account) public view returns (uint256) {
        uint256 balance = balanceOf(account);
        if (balance == 0) {
            return 0;
        }
        return convertStaticToDynamic(safe104(balance));
    }
```
Next, function `convertStaticToDynamic` is invoked.

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/compoundv3/CusdcV3Wrapper.sol#L241-L244

```solidity
    function convertStaticToDynamic(uint104 amount) public view returns (uint256) {
        (uint64 baseSupplyIndex, ) = getUpdatedSupplyIndicies();
        return presentValueSupply(baseSupplyIndex, amount);
    }
```
And next, function `getUpdatedSupplyIndicies` is invoked. As can be seen in its code logic, the returned value of `baseSupplyIndex_` is determined by the changing `supplyRate`.

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/compoundv3/CusdcV3Wrapper.sol#L298-L313

```solidity
    function getUpdatedSupplyIndicies() internal view returns (uint64, uint64) {
        TotalsBasic memory totals = underlyingComet.totalsBasic();
        uint40 timeDelta = uint40(block.timestamp) - totals.lastAccrualTime;
        uint64 baseSupplyIndex_ = totals.baseSupplyIndex;
        uint64 trackingSupplyIndex_ = totals.trackingSupplyIndex;
        if (timeDelta > 0) {
            uint256 baseTrackingSupplySpeed = underlyingComet.baseTrackingSupplySpeed();
            uint256 utilization = underlyingComet.getUtilization();
            uint256 supplyRate = underlyingComet.getSupplyRate(utilization);
            baseSupplyIndex_ += safe64(mulFactor(baseSupplyIndex_, supplyRate * timeDelta));
            trackingSupplyIndex_ += safe64(
                divBaseWei(baseTrackingSupplySpeed * timeDelta, totals.totalSupplyBase)
            );
        }
        return (baseSupplyIndex_, trackingSupplyIndex_);
    }
```
The returned value of `baseSupplyIndex` is then inputted into function `principalValueSupply` where the lower the value of `baseSupplyIndex`, the higher the `principalValueSupply` or simply put, the lesser the `burn` amount. 

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/compoundv3/CometHelpers.sol#L29-L35

```solidity
    function principalValueSupply(uint64 baseSupplyIndex_, uint256 presentValue_)
        internal
        pure
        returns (uint104)
    {
        return safe104((presentValue_ * BASE_INDEX_SCALE) / baseSupplyIndex_);
    }
```

## Tools Used
Manual

## Recommended Mitigation Steps
Consider implementing slippage protection on `CusdcV3Wrapper._withdraw` so that users could opt for the minimum amount of `comet` to receive or the maximum amount of `wComet` to burn.








## Assessed type

Timing
