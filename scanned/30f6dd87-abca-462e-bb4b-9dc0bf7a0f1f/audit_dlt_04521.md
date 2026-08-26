# [H] Pools cannot be initialized because of incorrectly used initializer modifier

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-float-capital
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/31
Type: sherlock-finding

## Details
obront

high

# Pools cannot be initialized because of incorrectly used initializer modifier

## Summary

The `MarketExtended.sol:initializePools()` function is called as a `delegatecall` from MarketCore.sol. This function has an `initializer` modifier, but MarketCore.sol will have already run a function with an `initializer` modifier. The result is that this function cannot be called, and pools cannot be initialized.

## Vulnerability Detail

The `initializer` modifier from OpenZeppelin only allows a function to be called once, and then writes the storage variable `_initialized = true` to ensure it is not called again.

```solidity
    modifier initializer() {
        bool isTopLevelCall = !_initializing;
        require(
            (isTopLevelCall && _initialized < 1) || (!AddressUpgradeable.isContract(address(this)) && _initialized == 1),
            "Initializable: contract is already initialized"
        );
        _initialized = 1;
        if (isTopLevelCall) {
            _initializing = true;
        }
        _;
        if (isTopLevelCall) {
            _initializing = false;
            emit Initialized(1);
        }
    }
```
Because the `initializePools()` function is called as a `delegatecall` from MarketCore.sol, it will operate on the storage of the calling contract. This storage already has an `_initialized` variable, which will have been set to `true` by the `initializer` modifier on MarketCore.sol's constructor.

[Here is a Gist with a copy & paste Forge test that can be used to verify the error.](https://gist.github.com/zobront/6103228bf131fa99ad658ef0f89a0e78)

## Impact


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/31_
