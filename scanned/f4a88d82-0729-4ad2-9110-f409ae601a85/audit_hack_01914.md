# [H] 6.1 FullMath Operation Correctness Issue

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Code Corrected

The FullMath.mulDiv(uint a, uint b, uint denominator) function performs the
floor(a×b÷denominator) operation. A similar function exists in the UniswapV3 core codebase.
However due to the change of the solidity compiler version from 0.7.6 to 0.8.9, some modifications
were made to account for the default SafeMath arithmetic operations behavior. This computation
happens in FullMath.mulDiv code:

```
prod0 := add(prod0, mul(prod1, twos))
```
While Uniswap library performs this operation:

```
prod0 |= prod1 * twos;
```
Please note that this operation occurs in the unchecked block.

As a result, the FullMath.mulDiv computation yields undesired results.

For example, this assignment of arguments causes overflow and panic in the FullMath.mulDiv.

```
a = 2**
b = 2**
denominator = 57896044618658100000000000000000000000000000000000000000000000000000000000001
```
The correct computation should yield 5789604461865809542357098500868799828994258986484
4074485766219939100404438900.


Code corrected:

The FullMath.mulDiv function has been replaced by the OpenZeppelin v4.8.0 implementation. It uses
Solidity compiler above 0.8.0 version.
