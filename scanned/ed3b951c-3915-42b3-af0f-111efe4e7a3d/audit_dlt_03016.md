# [M] deposit gas through depositGasAnycallConfig should not withdraw the nativeToken

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-maia
Published: 2023-07-05
Source: https://github.com/code-423n4/2023-05-maia-findings/issues/679
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-05-maia/blob/54a45beb1428d85999da3f721f923cbf36ee3d35/src/ulysses-omnichain/RootBridgeAgent.sol#L1219-L1222
https://github.com/code-423n4/2023-05-maia/blob/54a45beb1428d85999da3f721f923cbf36ee3d35/src/ulysses-omnichain/RootBridgeAgent.sol#L848-L852


# Vulnerability details

## Impact

DepositGasAnycallConfig can deposit the gas fee externally, but here should not withdraw the nativeToken. This prevents gas from being deposited.

## Proof of Concept

There are two ways to store gas in RootBridgeAgent:

```solidity
// deposit GAS
function _manageGasOut(uint24 _toChain) internal returns (uint128) {
    uint256 amountOut;
    address gasToken;
    uint256 _initialGas = initialGas;

    if (_toChain == localChainId) {
        //Transfer gasToBridgeOut Local Branch Bridge Agent if remote initiated call.
        if (_initialGas > 0) {
            address(wrappedNativeToken).safeTransfer(getBranchBridgeAgent[localChainId], userFeeInfo.gasToBridgeOut);
        }

        return uint128(userFeeInfo.gasToBridgeOut);
    }

    if (_initialGas > 0) {
        if (userFeeInfo.gasToBridgeOut <= MIN_FALLBACK_RESERVE * tx.gasprice) revert InsufficientGasForFees();
        (amountOut, gasToken) = _gasSwapOut(userFeeInfo.gasToBridgeOut, _toChain);
    } else {
        if (msg.value <= MIN_FALLBACK_RESERVE * tx.gasprice) revert InsufficientGasForFees();
        wrappedNativeToken.deposit{value: msg.value}();
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-maia-findings/issues/679_
