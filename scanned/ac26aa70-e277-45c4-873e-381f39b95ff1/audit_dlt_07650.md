# [?] fix: avoid false overflow on modexp lengths (#10360)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-02-18
Source: https://github.com/NethermindEth/nethermind/commit/bfd1994fd240cc398e37ea66d1cf5ca1412fdebb
Type: security-commit

## Details
fix: avoid false overflow on modexp lengths (#10360)

* fix: avoid false overflow on modexp lengths

* apply review suggestions

---------

Co-authored-by: Lukasz Rozmej <lukasz.rozmej@gmail.com>

## Patch
### src/Nethermind/Nethermind.Evm.Precompiles/ModExpPrecompile.cs
```diff
@@ -120,8 +120,8 @@ private static long DataGasCostInternal(ReadOnlySpan<byte> inputData, IReleaseSp
     private static bool ExceedsMaxInputSize(IReleaseSpec releaseSpec, uint baseLength, uint expLength, uint modulusLength)
     {
         return releaseSpec.IsEip7823Enabled
-            ? (baseLength > ModExpMaxInputSizeEip7823 | expLength > ModExpMaxInputSizeEip7823 | modulusLength > ModExpMaxInputSizeEip7823)
-            : (baseLength | modulusLength) >= uint.MaxValue;
+            ? (baseLength > ModExpMaxInputSizeEip7823 || expLength > ModExpMaxInputSizeEip7823 || modulusLength > ModExpMaxInputSizeEip7823)
+            : baseLength >= uint.MaxValue || modulusLength >= uint.MaxValue;
     }
 
     [MethodImpl(MethodImplOptions.NoInlining)]
```
