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

_Trimmed to 38 lines — full report: https://notes.ethereum.org/SMlCIdivQsCbMcyfORoLng_
