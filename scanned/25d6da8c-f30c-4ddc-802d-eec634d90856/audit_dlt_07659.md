# [?] Fix GetTrace crash when memory is not yet resized (#4957)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2022-12-05
Source: https://github.com/NethermindEth/nethermind/commit/e262197731eddbeb0adec62a35c531ededece59e
Type: security-commit

## Details
Fix GetTrace crash when memory is not yet resized (#4957)

## Patch
### src/Nethermind/Nethermind.Evm.Test/EvmPooledMemoryTests.cs
```diff
@@ -2,6 +2,7 @@
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using System;
+using FluentAssertions;
 using Nethermind.Core.Test.Builders;
 using Nethermind.Int256;
 using NUnit.Framework;
@@ -86,5 +87,13 @@ public void Load_should_update_size_of_memory()
             Assert.AreNotEqual(initialSize, memory.Size);
             Assert.AreEqual(expectedResult, result.ToArray());
         }
+
+        [Test]
+        public void GetTrace_should_not_thor_on_not_initialized_memory()
+        {
+            EvmPooledMemory memory = new();
+            memory.CalculateMemoryCost(0, 32);
+            memory.GetTrace().Should().BeEquivalentTo(new string[] { "0000000000000000000000000000000000000000000000000000000000000000" });
+        }
     }
 }
```

### src/Nethermind/Nethermind.Evm/EvmPooledMemory.cs
```diff
@@ -18,7 +18,7 @@ public class EvmPooledMemory : IEvmMemory
 
         private int _lastZeroedSize;
 
-        private byte[] _memory;
+        private byte[]? _memory;
         public ulong Length { get; private set; }
         public ulong Size { get; private set; }
 
@@ -29,7 +29,7 @@ public void SaveWord(in UInt256 location, Span<byte> word)
 
             if (word.Length < WordSize)
             {
-                Array.Clear(_memory, (int)location, WordSize - word.Length);
+                Array.Clear(_memory!, (int)location, WordSize - word.Length);
             }
 
             word.CopyTo(_memory.AsSpan((int)location + WordSize - word.Length, word.Length));
@@ -40,7 +40,7 @@ public void SaveByte(in UInt256 location, byte value)
             CheckMemoryAccessViolation(in location, WordSize);
             UpdateSize(in location, 1);
 
-            _memory[(long)location] = value;
+            _memory![(long)location] = value;
         }
 
         public void Save(in UInt256 location, Span<byte> value)
@@ -76,7 +76,7 @@ public void Save(in UInt256 location, byte[] value)
             CheckMemoryAccessViolation(in location, (UInt256)value.Length);
             UpdateSize(in location, (UInt256)value.Length);
 
-            Array.Copy(value, 0, _memory, (long)location, value.Length);
+            Array.Copy(value, 0, _memory!, (long)location, value.Length);
         }
 
         public void Save(in UInt256 location, ZeroPaddedSpan value)
@@ -205,14 +205,21 @@ public List<string> GetTrace()
         {
             int traceLocation = 0;
             List<string> memoryTrace = new();
-            if (_memory is not null)
+
+            while ((ulong)traceLocation < Size)
             {
-                while ((ulong)traceLocation < Size)
+                int sizeAvailable = Math.Min(WordSize, (_memory?.Length ?? 0) - traceLocation);
+                if (sizeAvailable > 0)
                 {
-                    int sizeAvailable = Math.Min(WordSize, (int)Size - traceLocation);
-                    memoryTrace.Add(_memory.Slice(traceLocation, sizeAvailable).ToHexString());
-                    traceLocation = traceLocation + WordSize;
+                    Span<byte> bytes = _memory.AsSpan().Slice(traceLocation, sizeAvailable);
+                    memoryTrace.Add(bytes.ToHexString());
                 }
+                else // Memory might not be initialized
+                {
+                    memoryTrace.Add(Bytes.Zero32.ToHexString());
+                }
+
+                traceLocation += WordSize;
             }
 
             return memoryTrace;
```
