# [M] Seer.get uses a view fetcher, breaking the intended use

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1184
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/oracle/Seer.sol#L52-L57
https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/oracle/OracleMulti.sol#L106-L109


# Vulnerability details

Seer.get is non-view because certain price sources can be attacked to return a manipulated value

A classic example would be Balancer Pools or Curve Pools

To combat that, `get` is non-view so that the call to the pool can also contain a no-op to trigger the reentrancy guard.

However, in the in-scope codebase, the call to `get` will use `_readAll`

https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/oracle/Seer.sol#L52-L57

```solidity
    /// @notice Get the latest exchange rate.
    /// For example:
    /// (string memory collateralSymbol, string memory assetSymbol, uint256 division) = abi.decode(data, (string, string, uint256));
    /// @return success if no valid (recent) rate is available, return false else true.
    /// @return rate The rate of the requested asset / pair / pool.
    function get( /// @audit This function is not-view to protect againt view-reentrancy but it's using a view `_readAll` 
        bytes calldata
    ) external virtual returns (bool success, uint256 rate) {
        (, uint256 high) = _readAll(inBase);
        return (true, high);
    }
```

`_readAll` is `view`

https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/oracle/OracleMulti.sol#L106-L109
```solidity
    function _readAll(
        uint256 quoteAmount
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1184_
