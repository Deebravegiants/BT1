# [?] Fix oob memory access in NibbleExtensions in certain scenarios (#10276)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-03-03
Source: https://github.com/NethermindEth/nethermind/commit/5599295526600b0b58b0539c4f5135b2b026c692
Type: security-commit

## Details
Fix oob memory access in NibbleExtensions in certain scenarios (#10276)

* Initial plan

* Gate intrinsic usage in benchmarks and document Blake2 methods

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Add Debug.Assert guard to Avx2Reverse256InPlace method

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Address code review: use exceptions instead of Debug.Assert for runtime safety

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Make Avx2Reverse256InPlace internal with Debug.Assert instead of runtime exceptions

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Fix NibbleExtensions Vector256.Shuffle to require AVX2 on x86 (fixes N5095 crash)

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Revert "Fix NibbleExtensions Vector256.Shuffle" - analysis was incorrect

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Fix critical out-of-bounds bug in NibbleExtensions causing v1.36.0 crashes

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Add comprehensive tests for BytesToNibbleBytes to detect out-of-bounds bugs

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Remove unnecessary offset on line 52 - processed is always 0 there

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Fix whitespace formatting in NibbleTests.cs

Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>

* Update src/Nethermind/Nethermind.Benchmark/Core/BytesReverseBenchmarks.cs

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: benaadams <1142958+benaadams@users.noreply.github.com>
Co-authored-by: Ben {chmark} Adams <thundercat@illyriad.co.uk>
Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

### src/Nethermind/Nethermind.Benchmark/Core/BytesReverseBenchmarks.cs
```diff
@@ -33,11 +33,14 @@ public class BytesReverseBenchmarks
         [GlobalSetup]
         public void Setup()
         {
-            unsafe
+            if (Avx2.IsSupported)
             {
-                fixed (byte* ptr_mask = _reverseMask)
+                unsafe
                 {
-                    _shuffleMask = Avx2.LoadVector256(ptr_mask);
+                    fixed (byte* ptr_mask = _reverseMask)
+                    {
+                        _shuffleMask = Avx2.LoadVector256(ptr_mask);
+                    }
                 }
             }
 
@@ -87,6 +90,11 @@ private static void Swap(Span<byte> bytes)
         [Benchmark]
         public void Avx2Version()
         {
+            if (!Avx2.IsSupported)
+            {
+                return;
+            }
+
             byte[] bytes = _a;
             unsafe
             {
```

### src/Nethermind/Nethermind.Core/Extensions/Bytes.Vector.cs
```diff
@@ -29,8 +29,12 @@ static Bytes()
         }
     }
 
-    public static void Avx2Reverse256InPlace(Span<byte> bytes)
+    // Internal method that requires AVX2 support - caller must check Avx2.IsSupported before calling
+    internal static void Avx2Reverse256InPlace(Span<byte> bytes)
     {
+        Debug.Assert(Avx2.IsSupported, "AVX2 must be supported to call Avx2Reverse256InPlace");
+        Debug.Assert(bytes.Length == 32, "Input must be exactly 32 bytes");
+
         fixed (byte* inputPointer = bytes)
         {
             Vector256<byte> inputVector = Avx2.LoadVector256(inputPointer);
```

### src/Nethermind/Nethermind.Crypto/Blake2/Blake2Avx2.cs
```diff
@@ -14,6 +14,8 @@ namespace Nethermind.Crypto.Blake2;
 public unsafe partial class Blake2Compression
 {
     // SIMD algorithm described in https://eprint.iacr.org/2012/275.pdf
+    // NOTE: This method uses AVX2 intrinsics without runtime checks.
+    // The caller (Compress method in Blake2Compression.cs) is responsible for checking Avx2.IsSupported.
     [MethodImpl(MethodImplOptions.AggressiveOptimization)]
     [SkipLocalsInit]
     private static void ComputeAvx2(ulong* sh, ulong* m, uint rounds)
```

### src/Nethermind/Nethermind.Crypto/Blake2/Blake2Sse41.cs
```diff
@@ -14,6 +14,8 @@ namespace Nethermind.Crypto.Blake2;
 public unsafe partial class Blake2Compression
 {
     // SIMD algorithm described in https://eprint.iacr.org/2012/275.pdf
+    // NOTE: This method uses SSE4.1 intrinsics without runtime checks.
+    // The caller (Compress method in Blake2Compression.cs) is responsible for checking Sse41.IsSupported.
     [MethodImpl(MethodImplOptions.AggressiveOptimization)]
     [SkipLocalsInit]
     private static void ComputeSse41(ulong* sh, ulong* m, uint rounds)
```

### src/Nethermind/Nethermind.Trie.Test/NibbleTests.cs
```diff
@@ -38,4 +38,235 @@ public void CompactDecodingTest()
             Nibbles.CompactToHexEncode(encoded).Should().BeEquivalentTo(_hexEncoding[i]);
         }
     }
+
+    [Test]
+    public void BytesToNibbleBytes_SmallInput_ProducesCorrectOutput()
+    {
+        // Test with small input that doesn't trigger vector paths
+        byte[] input = [0x12, 0x34, 0x56, 0x78];
+        byte[] expected = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08];
+
+        byte[] result = Nibbles.BytesToNibbleBytes(input);
+
+        result.Should().BeEquivalentTo(expected);
+    }
+
+    [Test]
+    public void BytesToNibbleBytes_Vector128Size_ProducesCorrectOutput()
+    {
+        // Test with 16 bytes - exactly one Vector128 chunk
+        byte[] input = new byte[16];
+        for (int i = 0; i < input.Length; i++)
+        {
+            input[i] = (byte)i;
+        }
+
+        byte[] result = Nibbles.BytesToNibbleBytes(input);
+
+        // Verify each byte was correctly split into two nibbles
+        for (int i = 0; i < input.Length; i++)
+        {
+            result[i * 2].Should().Be((byte)(input[i] >> 4), $"high nibble at position {i}");
+            result[i * 2 + 1].Should().Be((byte)(input[i] & 0x0F), $"low nibble at position {i}");
+        }
+    }
+
+    [Test]
+    public void BytesToNibbleBytes_LargerThanVector128_ProducesCorrectOutput()
+    {
+        // Test with 33 bytes - triggers multiple Vector128 iterations
+        // This would have caught the out-of-bounds bug where second iteration
+        // read from bytes[0] instead of bytes[processed]
+        // Use distinct values in each chunk to detect re-reading
+        byte[] input = new byte[33];
+        for (int i = 0; i < input.Length; i++)
+        {
+            // Use pattern: first 16 bytes = 0xA0-0xAF, next 16 = 0xB0-0xBF, last = 0xC0
+            if (i < 16)
+                input[i] = (byte)(0xA0 + i);
+            else if (i < 32)
+                input[i] = (byte)(0xB0 + (i - 16));
+            else
+                input[i] = 0xC0;
+        }
+
+        byte[] result = Nibbles.BytesToNibbleBytes(input);
+
+        result.Length.Should().Be(66);
+
+        // Verify each byte was correctly split into two nibbles
+        // With the bug, bytes 16-31 would have nibbles from bytes 0-15 instead
+        for (int i = 0; i < input.Length; i++)
+        {
+            byte expectedHigh = (byte)(input[i] >> 4);
+            byte expectedLow = (byte)(input[i] & 0x0F);
+
+            result[i * 2].Should().Be(expectedHigh, $"high nibble at position {i} (byte value 0x{input[i]:X2})");
+            result[i * 2 + 1].Should().Be(expectedLow, $"low nibble at position {i} (byte value 0x{input[i]:X2})");
+        }
+    }
+
+    [Test]
+    public void BytesToNibbleBytes_Vector256Size_ProducesCorrectOutput()
+    {
+        // Test with 32 bytes - exactly one Vector256 chunk (on AVX2 systems)
+        byte[] input = new byte[32];
+        for (int i = 0; i < input.Length; i++)
+        {
+            // Use values 0x10-0x2F to make nibbles distinct and non-zero
+            input[i] = (byte)(0x10 + i);
+        }
+
+        byte[] result = Nibbles.BytesToNibbleBytes(input);
+
+        result.Length.Should().Be(64);
+
+        // Verify each byte was correctly split into two nibbles
+        for (int i = 0; i < input.Length; i++)
+        {
+            result[i * 2].Should().Be((byte)(input[i] >> 4), $"high nibble at position {i}");
+            result[i * 2 + 1].Should().Be((byte)(input[i] & 0x0F), $"low nibble at position {i}");
+        }
+    }
+
+    [Test]
+    public void BytesToNibbleBytes_LargerThanVector256_ProducesCorrectOutput()
+    {
+        // Test with 65 bytes - triggers multiple Vector256 iterations on AVX2 systems
+        // This would have caught the out-of-bounds bug where second iteration
+        // read from bytes[0] instead of bytes[processed]
+        // Use distinct values in each chunk to detect re-reading
+        byte[] input = new byte[65];
+        for (int i = 0; i < input.Length; i++)
+        {
+            // Use pattern: first 32 bytes = 0x00-0x1F, next 32 = 0x20-0x3F, last = 0x40
+            if (i < 32)
+                input[i] = (byte)i;
+            else if (i < 64)
+                input[i] = (byte)(0x20 + (i - 32));
+            else
+                input[i] = 0x40;
+        }
+
+        byte[] result = Nibbles.BytesToNibbleBytes(input);
+
+        result.Length.Should().Be(130);
+
+        // Verify each byte was correctly split into two nibbles
+        // With the bug, bytes 32-63 would have nibbles from bytes 0-31 instead
+        for (int i = 0; i < input.Length; i++)
+        {
+            byte expectedHigh = (byte)(input[i] >> 4);
+            byte expectedLow = (byte)(input[i] & 0x0F);
+
+            result[i * 2].Should().Be(expectedHigh, $"high nibble at position {i} (byte value 0x{input[i]:X2})");
+            result[i * 2 + 1].Should().Be(expectedLow, $"low nibble at position {i} (byte value 0x{input[i]:X2})");
+        }
+    }
+
+    [Test]
+    public void BytesToNibbleBytes_Vector256ThenVector128_ProducesCorrectOutput()
+    {
+        // Test with 80 bytes - on AVX2 systems this triggers:
+        // - Vector256 processes 64 bytes (2 iterations of 32 bytes)
+        // - Vector128 processes remaining 16 bytes
+        // With the bug, Vector128 would read from bytes[0] instead of bytes[64]
+        byte[] input = new byte[80];
+        for (int i = 0; i < input.Length; i++)
+        {
+            // Each byte has a unique pattern so we can detect misread data
+            input[i] = (byte)(i % 256);
+        }
+
+        byte[] result = Nibbles.BytesToNibbleBytes(input);
+
+        result.Length.Should().Be(160);
+
+        // Verify each byte was correctly split into two nibbles
+        // With the bug, bytes 64-79 would show nibbles from bytes 0-15
+        for (int i = 0; i < input.Length; i++)
+        {
+            byte expectedHigh = (byte)(input[i] >> 4);
+            byte expectedLow = (byte)(input[i] & 0x0F);
+
+            result[i * 2].Should().Be(expectedHigh,
+                $"high nibble at position {i} (byte value 0x{input[i]:X2}, expected from input[{i}])");
+            result[i * 2 + 1].Should().Be(expectedLow,
+                $"low nibble at position {i} (byte value 0x{input[i]:X2}, expected from input[{i}])");
+        }
+    }
+
+    [Test]
+    public void BytesToNibbleBytes_MultipleVector128Iterations_ProducesCorrectOutput()
+    {
+        // Test with 48 bytes - triggers 3 Vector128 iterations (16 bytes each)
+        // With the bug, second and third iterations would read from wrong offset
+        byte[] input = new byte[48];
+        for (int i = 0; i < input.Length; i++)
+        {
+            // Each 16-byte chunk has distinct values
+            input[i] = (byte)((i / 16) * 64 + (i % 16));
+        }
+
+        byte[] result = Nibbles.BytesToNibbleBytes(input);
+
+        result.Length.Should().Be(96);
+
+        // Verify each byte was correctly split
+        for (int i = 0; i < input.Length; i++)
+        {
+            byte expectedHigh = (byte)(input[i] >> 4);
+            byte expectedLow = (byte)(input[i] & 0x0F);
+
+            result[i * 2].Should().Be(expectedHigh,
+                $"high nibble at position {i} (byte value 0x{input[i]:X2})");
+            result[i * 2 + 1].Should().Be(expectedLow,
+                $"low nibble at position {i} (byte value 0x{input[i]:X2})");
+        }
+    }
+
+    [Test]
+    public void BytesToNibbleBytes_LargeInput_ProducesCorrectOutput()
+    {
+        // Test with 128 bytes - ensures multiple iterations of vector code
+        // and tests boundary conditions
+        byte[] input = new byte[128];
+        for (int i = 0; i < input.Length; i++)
+        {
+            input[i] = (byte)(i % 256);
+        }
+
+        byte[] result = Nibbles.BytesToNibbleBytes(input);
+
+        result.Length.Should().Be(256);
+
+        // Verify each byte was correctly split into two nibbles
+        for (int i = 0; i < input.Length; i++)
+        {
+            result[i * 2].Should().Be((byte)(input[i] >> 4), $"high nibble at position {i}");
+            result[i * 2 + 1].Should().Be((byte)(input[i] & 0x0F), $"low nibble at position {i}");
+        }
+    }
+
+    [Test]
+    public void BytesToNibbleBytes_AllByteValues_ProducesCorrectOutput()
+    {
+        // Test with all possible byte values to ensure correctness
+        byte[] input = new byte[256];
+        for (int i = 0; i < 256; i++)
+        {
+            input[i] = (byte)i;
+        }
+
+        byte[] result = Nibbles.BytesToNibbleBytes(input);
+
+        result.Length.Should().Be(512);
+
+        // Verify each byte was correctly split into two nibbles
+        for (int i = 0; i < input.Length; i++)
+        {
+            result[i * 2].Should().Be((byte)(input[i] >> 4), $"high nibble at position {i}");
+            result[i * 2 + 1].Should().Be((byte)(input[i] & 0x0F), $"low nibble at position {i}");
+        }
+    }
 }
```

### src/Nethermind/Nethermind.Trie/NibbleExtensions.cs
```diff
@@ -93,7 +93,7 @@ public static void BytesToNibbleBytes(ReadOnlySpan<byte> bytes, Span<byte> nibbl
             if (Vector128.IsHardwareAccelerated && length > 0)
             {
                 // Cast the byte span to a span of Vector128<byte> for SIMD processing.
-                ReadOnlySpan<Vector128<byte>> input = MemoryMarshal.CreateReadOnlySpan(ref Unsafe.As<byte, Vector128<byte>>(ref MemoryMarshal.GetReference(bytes)), length);
+                ReadOnlySpan<Vector128<byte>> input = MemoryMarshal.CreateReadOnlySpan(ref Unsafe.As<byte, Vector128<byte>>(ref Unsafe.Add(ref MemoryMarshal.GetReference(bytes), processed)), length);
                 length *= Vector128<byte>.Count;
                 // Cast the nibble span to a reference to first element of Vector128<ushort> as input doubles.
                 ref Vector128<ushort> output = ref Unsafe.As<byte, Vector128<ushort>>(ref Unsafe.Add(ref MemoryMarshal.GetReference(nibbles), processed * 2));
```
