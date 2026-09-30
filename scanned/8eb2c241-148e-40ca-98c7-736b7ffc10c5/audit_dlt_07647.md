# [?] fix(zkevm): Fatal stack-underflow halt in the zkEVM guest (#12064)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-06-21
Source: https://github.com/NethermindEth/nethermind/commit/22be4a487e9725749619268b7af5989de9d0cede
Type: security-commit

## Details
fix(zkevm): Fatal stack-underflow halt in the zkEVM guest (#12064)

## Patch
### src/Nethermind/Nethermind.Core/Crypto/KeccakCache.cs
```diff
@@ -40,39 +40,37 @@ public static unsafe class KeccakCache
     private const int InputLengthOfAddress = Address.Size;
     private const int CacheLineSizeBytes = 64;
 
-#if ZK_EVM
-    // zkEVM: avoid NativeMemory.AlignedAlloc (can fault in some environments). Use managed pinned storage instead.
-    private static readonly byte[] ManagedBuffer;
-    private static readonly GCHandle ManagedHandle;
-#endif
+#if !ZK_EVM
     private static readonly Entry* Memory;
 
     static KeccakCache()
     {
         const nuint size = Count * Entry.Size;
 
-#if ZK_EVM
-        ManagedBuffer = GC.AllocateArray<byte>((int)size, pinned: true);
-        ManagedHandle = GCHandle.Alloc(ManagedBuffer, GCHandleType.Pinned);
-        Memory = (Entry*)ManagedHandle.AddrOfPinnedObject();
-#else
         // Aligned, so that no torn reads if fields of Entry are properly aligned.
         Memory = (Entry*)NativeMemory.AlignedAlloc(size, BitOperations.RoundUpToPowerOf2(Entry.Size));
         NativeMemory.Clear(Memory, size);
         GC.AddMemoryPressure((long)size);
-#endif
     }
+#endif
 
     [SkipLocalsInit]
     public static ValueHash256 Compute(ReadOnlySpan<byte> input)
     {
+#if ZK_EVM
+        return input.IsEmpty ? ValueKeccak.OfAnEmptyString : ValueKeccak.Compute(input);
+#else
         ComputeTo(input, out ValueHash256 keccak256);
         return keccak256;
+#endif
     }
 
     [SkipLocalsInit]
     public static void ComputeTo(ReadOnlySpan<byte> input, out ValueHash256 keccak256)
     {
+#if ZK_EVM
+        keccak256 = input.IsEmpty ? ValueKeccak.OfAnEmptyString : ValueKeccak.Compute(input);
+#else
         // Special cases jump forward as unpredicted
         if (input.Length is 0 or > Entry.MaxPayloadLength)
         {
@@ -207,6 +205,7 @@ public static void ComputeTo(ReadOnlySpan<byte> input, out ValueHash256 keccak25
 
     Uncommon:
         keccak256 = input.Length == 0 ? ValueKeccak.OfAnEmptyString : ValueKeccak.Compute(input);
+#endif
     }
 
     /// <summary>
```

### src/Nethermind/Nethermind.Evm.Precompiles/zkevm/ModExpPrecompile.cs
```diff
@@ -30,11 +30,14 @@ public partial Result<byte[]> Run(ReadOnlyMemory<byte> inputData, IReleaseSpec r
         uint expStart = expOffset > uint.MaxValue ? uint.MaxValue : (uint)expOffset;
         uint modulusStart = modulusOffset > uint.MaxValue ? uint.MaxValue : (uint)modulusOffset;
 
-        ReadOnlySpan<byte> @base = inputSpan.SliceWithZeroPaddingEmptyOnError(96U, baseLength);
-        ReadOnlySpan<byte> exp = inputSpan.SliceWithZeroPaddingEmptyOnError(expStart, expLength);
         ReadOnlySpan<byte> modulus = inputSpan.SliceWithZeroPaddingEmptyOnError(modulusStart, modulusLength);
         byte[] result = new byte[modulusLength];
 
+        if (modulus.IsEmpty || modulus.IndexOfAnyExcept((byte)0) < 0)
+            return result;
+
+        ReadOnlySpan<byte> @base = inputSpan.SliceWithZeroPaddingEmptyOnError(96U, baseLength);
+        ReadOnlySpan<byte> exp = inputSpan.SliceWithZeroPaddingEmptyOnError(expStart, expLength);
         Accelerators.ModExp(@base, exp, modulus, result);
 
         return result;
```

### src/Nethermind/Nethermind.Evm.Test/StackUnderflowRegressionTests.cs
```diff
@@ -0,0 +1,33 @@
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
+// SPDX-License-Identifier: LGPL-3.0-only
+
+using Nethermind.Specs;
+using NUnit.Framework;
+
+namespace Nethermind.Evm.Test;
+
+public class StackUnderflowRegressionTests : VirtualMachineTestsBase
+{
+    protected override long BlockNumber => MainnetSpecProvider.ParisBlockNumber;
+    protected override ulong Timestamp => MainnetSpecProvider.CancunBlockTimestamp;
+
+    // Each case leaves the stack exactly one item short of what the opcode's converted pop needs:
+    // the preceding pops succeed, then the value/topic/salt pop underflows.
+    private static readonly object[] UnderflowCases =
+    [
+        new object[] { Instruction.BYTE, Prepare.EvmCode.PushData(0).Op(Instruction.BYTE).Done },
+        new object[] { Instruction.SSTORE, Prepare.EvmCode.PushData(0).Op(Instruction.SSTORE).Done },
+        new object[] { Instruction.TSTORE, Prepare.EvmCode.PushData(0).Op(Instruction.TSTORE).Done },
+        new object[] { Instruction.LOG1, Prepare.EvmCode.PushData(0).PushData(0).Op(Instruction.LOG1).Done },
+        new object[] { Instruction.CREATE2, Prepare.EvmCode.PushData(0).PushData(0).PushData(0).Op(Instruction.CREATE2).Done },
+        // Index 0 is in-range, so SIGNEXTEND skips the out-of-range short-circuit and peeks the missing value.
+        new object[] { Instruction.SIGNEXTEND, Prepare.EvmCode.PushData(0).Op(Instruction.SIGNEXTEND).Done },
+    ];
+
+    [TestCaseSource(nameof(UnderflowCases))]
+    public void Signals_stack_underflow_when_final_operand_missing(Instruction opcode, byte[] code)
+    {
+        TestAllTracerWithOutput result = Execute(code);
+        Assert.That(result.Error, Is.EqualTo(EvmExceptionType.StackUnderflow.ToString()), opcode.ToString());
+    }
+}
```

### src/Nethermind/Nethermind.Evm/Instructions/EvmInstructions.Create.cs
```diff
@@ -101,7 +101,8 @@ public static EvmExceptionType InstructionCreate<TGasPolicy, TOpCreate, TTracing
         // For CREATE2, an extra salt value is required. Use type check to differentiate.
         if (typeof(TOpCreate) == typeof(OpCreate2))
         {
-            salt = stack.PopWord256();
+            if (!stack.PopWord256(out salt))
+                goto StackUnderflow;
         }
 
         // EIP-3860: Limit the maximum size of the initialization code.
```

### src/Nethermind/Nethermind.Evm/Instructions/EvmInstructions.Math1Param.cs
```diff
@@ -121,7 +121,8 @@ public static EvmExceptionType InstructionByte<TGasPolicy, TTracingInst>(Virtual
         // Pop the byte position and the 256-bit word.
         if (!stack.PopUInt256(out UInt256 a))
             goto StackUnderflow;
-        Span<byte> bytes = stack.PopWord256();
+        if (!stack.PopWord256(out Span<byte> bytes))
+            goto StackUnderflow;
 
         // If the position is out-of-range, push zero. Using direct limb access avoids the
         // full 256-bit vector compare + defensive `in` copy the JIT emits for `a >= BigInt32`,
@@ -165,7 +166,11 @@ public static EvmExceptionType InstructionSignExtend<TGasPolicy>(VirtualMachine<
         int position = 31 - (int)a;
 
         // Peek at the 256-bit word without removing it.
-        Span<byte> bytes = stack.PeekWord256();
+        ref byte bytesRef = ref stack.PeekBytesByRef();
+        if (IsNullRef(ref bytesRef))
+            goto StackUnderflow;
+
+        Span<byte> bytes = MemoryMarshal.CreateSpan(ref bytesRef, EvmStack.WordSize);
         sbyte sign = (sbyte)bytes[position];
 
         // Extend the sign by replacing higher-order bytes.
```

### src/Nethermind/Nethermind.Evm/Instructions/EvmInstructions.Stack.cs
```diff
@@ -1103,7 +1103,8 @@ public static EvmExceptionType InstructionLog<TGasPolicy, TOpCount>(VirtualMachi
         Hash256[] topics = new Hash256[topicsCount];
         for (int i = 0; i < topics.Length; i++)
         {
-            topics[i] = new Hash256(stack.PopWord256());
+            if (!stack.PopWord256(out Span<byte> topic)) goto StackUnderflow;
+            topics[i] = new Hash256(topic);
         }
 
         // Create a new log entry with the executing account, log data, and topics.
```

### src/Nethermind/Nethermind.Evm/Instructions/EvmInstructions.Storage.cs
```diff
@@ -104,7 +104,7 @@ public static EvmExceptionType InstructionTStore<TGasPolicy>(VirtualMachine<TGas
         StorageCell storageCell = new(vmState.Env.ExecutingAccount, in result);
 
         // Pop the 32-byte value from the stack.
-        Span<byte> bytes = stack.PopWord256();
+        if (!stack.PopWord256(out Span<byte> bytes)) goto StackUnderflow;
 
         // Store either the actual value (if non-zero) or a predefined zero constant.
         vm.WorldState.SetTransientState(in storageCell, !bytes.IsZero() ? bytes.ToArray() : BytesZero32);
@@ -370,7 +370,8 @@ internal static EvmExceptionType InstructionSStoreUnmetered<TGasPolicy, TTracing
 
         // Pop the key and then the new value for storage; signal underflow if unavailable.
         if (!stack.PopUInt256(out UInt256 result)) goto StackUnderflow;
-        ReadOnlySpan<byte> bytes = stack.PopWord256();
+        if (!stack.PopWord256(out Span<byte> bytesSpan)) goto StackUnderflow;
+        ReadOnlySpan<byte> bytes = bytesSpan;
 
         // Determine if the new value is effectively zero and normalize non-zero values by stripping leading zeros.
         bool newIsZero = bytes.IsZero();
@@ -484,7 +485,8 @@ internal static EvmExceptionType InstructionSStoreMetered<TGasPolicy, TTracingIn
 
         // Pop the key and then the new value for storage; signal underflow if unavailable.
         if (!stack.PopUInt256(out UInt256 result)) goto StackUnderflow;
-        ReadOnlySpan<byte> bytes = stack.PopWord256();
+        if (!stack.PopWord256(out Span<byte> bytesSpan)) goto StackUnderflow;
+        ReadOnlySpan<byte> bytes = bytesSpan;
 
         // Determine if the new value is effectively zero and normalize non-zero values by stripping leading zeros.
         bool newIsZero = bytes.IsZero();
```

### src/Nethermind/Nethermind.Evm/VirtualMachine.zkevm.cs
```diff
@@ -11,10 +11,25 @@ public unsafe partial class VirtualMachine<TGasPolicy> where TGasPolicy : struct
 {
     private delegate*<VirtualMachine<TGasPolicy>, ref EvmStack, ref TGasPolicy, ref int, EvmExceptionType>[] _opcodeMethods;
 
-    // For tracing-enabled execution, generate (if necessary) and cache the traced opcode set.
-    private partial void PrepareOpcodes<TTracingInst>(IReleaseSpec spec) where TTracingInst : struct, IFlag =>
-        _opcodeMethods = (delegate*<VirtualMachine<TGasPolicy>, ref EvmStack, ref TGasPolicy, ref int, EvmExceptionType>[])(spec.EvmInstructionsTraced ??= GenerateOpCodes<TTracingInst>(spec));
+    // Select and lazily build the opcode dispatch table for the active tracing mode, caching each
+    // mode separately on the spec. Mirrors the std build minus its periodic PGO-driven cache refresh,
+    // which is moot for the AOT-compiled guest.
+    private partial void PrepareOpcodes<TTracingInst>(IReleaseSpec spec) where TTracingInst : struct, IFlag
+    {
+        if (!TTracingInst.IsActive)
+        {
+            _opcodeMethods =
+                (delegate*<VirtualMachine<TGasPolicy>, ref EvmStack, ref TGasPolicy, ref int, EvmExceptionType>[])
+                (spec.EvmInstructionsNoTrace ??= GenerateOpCodes<TTracingInst>(spec));
+        }
+        else
+        {
+            _opcodeMethods =
+                (delegate*<VirtualMachine<TGasPolicy>, ref EvmStack, ref TGasPolicy, ref int, EvmExceptionType>[])
+                (spec.EvmInstructionsTraced ??= GenerateOpCodes<TTracingInst>(spec));
+        }
+    }
 
     protected delegate*<VirtualMachine<TGasPolicy>, ref EvmStack, ref TGasPolicy, ref int, EvmExceptionType>[] GenerateOpCodes<TTracingInst>(IReleaseSpec spec) where TTracingInst : struct, IFlag =>
-        EvmInstructions.GenerateOpCodes<TGasPolicy, OffFlag>(spec);
+        EvmInstructions.GenerateOpCodes<TGasPolicy, TTracingInst>(spec);
 }
```
