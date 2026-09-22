# [M] EL-2022-06: modexp gas calculation consensus bug

## Summary
Severity: Medium
Chain: Ethereum (execution layer)
Component: Nethermind
Published: 2023-05-03
Source: https://notes.ethereum.org/SMlCIdivQsCbMcyfORoLng
Type: ef-disclosure

## Details
# modexp gas calculation consensus bug

## Nethermind

**TLDR:** Nethermind has a consensus issue in the gas calculation for modexp.

**Disclaimer:** I have manually verified this by adding a test case in `Nethermind.Evm.Test.Eip2565Tests`, but I am not a seasoned .NET developer and it may be wrong.

### Attack

Send specific data to the modexp precompile.

### Impact

Consensus bug between Nethermind and Geth.

### Components

Nethermind 1.13.3. However the code seems to be identical since 1.10.56, and likely several older versions.

### Details

`0000000000000000000000000000000000000000000000000000000000000001200000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000010001`

This input to the modexp precompile causes an internal gas calculation overflow in Nethermind and results in a final gas cost of 200.  It is supposed to result in OOG, which it does on geth and besu.

The [DataGasCost](https://github.com/NethermindEth/nethermind/blob/master/src/Nethermind/Nethermind.Evm/Precompiles/ModExpPrecompile.cs#L56) code parses these inputs into `expLength=0x2000000000000000000000000000000000000000000000000000000000000020, exp=1`. Here note that due [`expLength` being truncated to 32](https://github.com/NethermindEth/nethermind/blob/master/src/Nethermind/Nethermind.Evm/Precompiles/ModExpPrecompile.cs#L77), the value of `exp` will be read from a valid location resulting in `exp=1`.

The actual overflow takes place in [CalculateIterationCount](https://github.com/NethermindEth/nethermind/blob/master/src/Nethermind/Nethermind.Evm/Precompiles/ModExpPrecompile.cs#L202):
```
                    int bitLength = (exponent & UInt256.MaxValue).BitLen;
                    if (bitLength > 0)
                    {
                        bitLength--;
                    }

                    iterationCount = 8 * (exponentLength - 32) + (UInt256)bitLength;
```

Here with `exp=1` we get `bitLength=0`.

The multiplication takes place within the int256 library, see [`operator *`](https://github.com/NethermindEth/int256/blob/master/src/Nethermind.Int256/UInt256.cs#L1457) and [`Multiply()`](https://github.com/NethermindEth/int256/blob/master/src/Nethermind.Int256/UInt256.cs#L783), both of which do not report overflows. Hence the `catch (OverflowException)` around the `iterationCount` is not triggered.

Notice that our special inputs will result in `2^256` which is above the range of `[0, 2^256-1]`.

Since this overflows and results in 0, the `CalculateIterationCount` function will return `1`:
```
return UInt256.Max(iterationCount, UInt256.One);
```

Circling back to the final cost calculation:
```
return Math.Max(200L, (long)(complexity * iterationCount / 3));
```

Since `complexity` and `iterationCount` are both `1`, we end up with 200 gas.

### Fix

1. Have a special case for infeasible lengths (i.e. >2^32-1) and early abort with OOG.
2. Use overflow checked multiplication in `CalculateIterationCount`.

## Geth

Additionally there is a slight "bug" in geth's modexp implementation as well, but as long as gas calculation precedes it, it should not be exploitable.

The truncation problem in geth doesn't affect the gas calculation, but the following input will result in an unexpected output of `01`:

`0000000000000000000000000000000000000000000000000000000000000001f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018080`

Geth uses `.Uint64()` on the input value, which has [undefined behaviour](https://pkg.go.dev/math/big#Int.Uint64) on overflow, and will ignore (at least on Apple M1) the high bits above 2^64-1. This in fact triggered my search in other clients, like Nethermind.

The [base.Exp(...)](https://github.com/ethereum/go-ethereum/blob/master/core/vm/contracts.go#L388) expression will use the truncated inputs of `base=1,exp=0,mod=1`, however `exp` should be `0xf000000000000000000000000000000000000000000000000000000000000000` long and `mod` would need to be at the trail of that infeasibly large calldata.
