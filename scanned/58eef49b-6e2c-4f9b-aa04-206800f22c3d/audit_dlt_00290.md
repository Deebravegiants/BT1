# [M] EL-2022-13: Nethermind ModExp Consensus Failure (OutOfMemory Exception)

## Summary
Severity: Medium
Chain: Ethereum (execution layer)
Component: Nethermind
Published: 2023-05-03
Source: https://gist.github.com/pleasew8t/734fb76304bf8375b60cfc9b46cc9351
Type: ef-disclosure

## Details
## Description

An issue was identified within the Nethermind Ethereum client’s execution layer that could be abused to cause a consensus break from other Ethereum clients. The issue was found in Nethermind’s implementation of the `ModExp` precompile (address `0x5`) and introduced in commit [956658e](https://github.com/NethermindEth/nethermind/commit/956658ef2fec18edda55510931489d5cd3ea1bb1), which is expected to be included in the next release.

The first 96 bytes of the payload for the `ModExp` precompile consists of the `base length`, `exponent length`, and the `modulus length`, which are used to indicate how many bytes to read after the first 96 bytes to retrieve the `base`, `exponent` and `modulus` terms. An excerpt of this logic is shown below, taken from the `GetInputLengths()` function at [ModExpPrecompile.cs#L104](https://github.com/NethermindEth/nethermind/blob/220cc8a077c99ce304f08fce7769872259588f87/src/Nethermind/Nethermind.Evm/Precompiles/ModExpPrecompile.cs#L104)

```csharp
int baseLength = (int)new UInt256(extendedInput.Slice(0, 32), true);
UInt256 expLengthUint256 = new(extendedInput.Slice(32, 32), true);
int expLength = expLengthUint256 > int.MaxValue ? 
                        int.MaxValue : (int)expLengthUint256;
int modulusLength = (int)new UInt256(extendedInput.Slice(64, 32), true);
```

Using these values, the precompile implementation will then proceed to creating memory buffers of sizes `baseLength`, `expLength`, and `modulusLength`, and copy the specified amount of data from the input buffer at different offsets. This is shown in the excerpt below, taken from the `Run()` function at [ModExpPrecompile.cs#L118](https://github.com/NethermindEth/nethermind/blob/220cc8a077c99ce304f08fce7769872259588f87/src/Nethermind/Nethermind.Evm/Precompiles/ModExpPrecompile.cs#L118)

```csharp
(int baseLength, int expLength, int modulusLength) = GetInputLengths(inputData);

byte[] modulusData = inputData.Span.SliceWithZeroPaddingEmptyOnError(
         96 + baseLength + expLength, modulusLength);
using mpz_t modulusInt = ImportDataToGmp(modulusData);

byte[] baseData = inputData.Span.SliceWithZeroPaddingEmptyOnError(
         96, baseLength);
using mpz_t baseInt = ImportDataToGmp(baseData);

byte[] expData = inputData.Span.SliceWithZeroPaddingEmptyOnError(
          96 + baseLength, expLength);
using mpz_t expInt = ImportDataToGmp(expData);

if (gmp_lib.mpz_sgn(modulusInt) == 0)
{
   return (new byte[modulusLength], true);
}
```

In the above code, the call to `SliceWithZeroPaddingEmptyOnError()` does the following:

_Trimmed to 38 lines — full report: https://gist.github.com/pleasew8t/734fb76304bf8375b60cfc9b46cc9351_
