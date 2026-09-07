# [M] `CTokenV3Collateral._underlyingRefPerTok` should use the decimals from underlying Comet.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/39
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/compoundv3/CTokenV3Collateral.sol#L56
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/compoundv3/CusdcV3Wrapper.sol#L46
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/compoundv3/CusdcV3Wrapper.sol#L236


# Vulnerability details

## Impact

`CTokenV3Collateral._underlyingRefPerTok` uses `erc20Decimals` which is the decimals of `CusdcV3Wrapper`. But it should use the decimals of the underlying Comet.

## Proof of Concept

CTokenV3Collateral._underlyingRefPerTok` computes the actual quantity of whole reference units per whole collateral tokens. And it passes `erc20Decimals` to `shiftl_toFix`
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/compoundv3/CTokenV3Collateral.sol#L56
```solidity
    function _underlyingRefPerTok() internal view virtual override returns (uint192) {
        return shiftl_toFix(ICusdcV3Wrapper(address(erc20)).exchangeRate(), -int8(erc20Decimals));
    }
```

However, the correct decimals should be the decimals of underlying Comet since it is used in `CusdcV3Wrapper.exchangeRate`
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/compoundv3/CusdcV3Wrapper.sol#L236
```solidity
    function exchangeRate() public view returns (uint256) {
        (uint64 baseSupplyIndex, ) = getUpdatedSupplyIndicies();
        return presentValueSupply(baseSupplyIndex, safe104(10**underlyingComet.decimals()));
    }
```


## Tools Used

Manual Review

## Recommended Mitigation Steps

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-reserve-findings/issues/39_
