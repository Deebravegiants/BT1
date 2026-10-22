# [M] sqrtPX96 can be manipulated to inflate or deflate pool launch price

## Summary
Severity: Medium
Contest weight: 0.4111
Dataset id: 3132
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _createUniswapV3Pool() function uses the quoteExactInput() function to retrieve the dragonXAmount. This is used alongside the ascendantAmount to determine the sqrtPX96 to be used as the initialization price for the dragonX-ascendant pool. The issue with this is that the dragonXAmount returned from the quoteExactInput() call is manipulable since it retrieves the amount from a simulated swap (Quoter.sol). Due to this, an attacker can inflate or deflate the sqrtPriceX96 initialization value to be way higher or lower than expected. This makes the launch un-guarded since anyone can control the launch price.
```solidity
uint256 dragonXAmount = quoter.quoteExactInput(path, INITIAL_TITAN_X_FOR_LIQ);
uint256 ascendantAmount = INITIAL_ASCENDANT_FOR_LP;
(address token0, address token1) = _ascendant < _dragonX ? (_ascendant, _dragonX) : (_dragonX, _ascendant);
(uint256 amount0, uint256 amount1) = token0 == _dragonX ? (dragonXAmount, ascendantAmount) : (ascendantAmount, dragonXAmount);
uint160 sqrtPX96 = uint160((sqrt((amount1 * 1e18) / amount0) * 2 ** 96) / 1e9);
```

## Recommendation
Consider using the TWAP price using OracleLib.sol.
