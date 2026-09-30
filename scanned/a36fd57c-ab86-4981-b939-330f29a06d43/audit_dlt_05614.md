# [?] fix: IByteBuffer leak in EnrResponseMsgSerializer & ArrayPoolSpan OOB (#10853)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-03-18
Source: https://github.com/NethermindEth/nethermind/commit/fca448c9239e5dfb6edbb743c443b6b3d3b3e460
Type: security-commit

## Details
fix: IByteBuffer leak in EnrResponseMsgSerializer & ArrayPoolSpan OOB (#10853)

* fix leak & array oob

* add leak detector

* Add claude rule

* remove docs

* fix formatting & add allocator cost note to LeakDetector

* fix: address PR review feedback

- ArrayPoolSpan.Slice: validate against logical length, not rented array
- ArrayPoolSpan indexer: add nameof(index) to ThrowIfGreaterThanOrEqual
- Add Slice tests: boundary, out-of-range, and logical length enforcement
- PooledBufferLeakDetector: add AssertNoLeaks() for explicit assertion,
  make Dispose() non-throwing to avoid masking test-body exceptions
- Add explicit FluentAssertions package reference to Discovery.Test csproj
- Add buffer refcount leak tests for all discovery message serializers
  (Ping, Pong, FindNode, Neighbors, EnrResponse — happy and error paths)
- Fix leak test: use ReferenceCount check instead of PooledBufferLeakDetector
  (pool NumActiveAllocations metric is unreliable with zero-cache config)

---------

Co-authored-by: Ben Adams <thundercat@illyriad.co.uk>

## Patch
### .agents/rules/robustness.md
```diff
@@ -12,6 +12,7 @@ Patterns that cause silent failures, resource leaks, or deadlocks in production.
 ## Resource management
 
 - `IDisposable` / `IAsyncDisposable` objects (especially `IDb`, streams, channels) must be wrapped in `using` — otherwise they leak.
+- `ReadBytes(n)` allocates a new ref-counted `IByteBuffer`. The method that allocates the buffer owns it; if ownership transfers (e.g. passing to a handler or message), the receiver becomes responsible for calling `Release()` / `SafeRelease()`. Forgetting to release, or releasing after ownership has transferred, are the two most common leak/corruption sources in the networking layer.
 - Never swallow exceptions in an empty `catch` block — at minimum log the exception. Silent failures are the hardest to diagnose on a running node.
 
 ## Thread safety
```

### src/Nethermind/Nethermind.Core.Test/Collections/ArrayPoolSpanTests.cs
```diff
@@ -0,0 +1,118 @@
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
+// SPDX-License-Identifier: LGPL-3.0-only
+
+using System;
+using FluentAssertions;
+using Nethermind.Core.Collections;
+using NUnit.Framework;
+
+namespace Nethermind.Core.Test.Collections;
+
+public class ArrayPoolSpanTests
+{
+    [TestCase(8, 8, Description = "At index == Length")]
+    [TestCase(4, 5, Description = "Beyond Length")]
+    public void Indexer_out_of_bounds_should_throw(int length, int index)
+    {
+        using ArrayPoolSpan<int> span = new(length);
+        span.Invoking(s => { int _ = s[index]; }).Should().Throw<ArgumentOutOfRangeException>();
+    }
+
+    [TestCase(4, -1)]
+    [TestCase(8, -5)]
+    public void Indexer_negative_should_throw(int length, int index)
+    {
+        using ArrayPoolSpan<int> span = new(length);
+        span.Invoking(s => { int _ = s[index]; }).Should().Throw<IndexOutOfRangeException>();
+    }
+
+    [Test]
+    public void Indexer_within_bounds_should_round_trip()
+    {
+        using ArrayPoolSpan<int> span = new(4);
+        span[0] = 10;
+        span[3] = 40;
+        span[0].Should().Be(10);
+        span[3].Should().Be(40);
+    }
+
+    [TestCase(0)]
+    [TestCase(1)]
+    [TestCase(7)]
+    [TestCase(16)]
+    public void Length_should_return_requested_size(int length)
+    {
+        using ArrayPoolSpan<int> span = new(length);
+        span.Length.Should().Be(length);
+    }
+
+    [Test]
+    public void Implicit_span_conversion_should_respect_length()
+    {
+        using ArrayPoolSpan<int> span = new(4);
+        for (int i = 0; i < 4; i++) span[i] = i;
+
+        Span<int> s = span;
+        s.Length.Should().Be(4);
+        s[0].Should().Be(0);
+        s[3].Should().Be(3);
+    }
+
+    [Test]
+    public void Implicit_readonly_span_conversion_should_respect_length()
+    {
+        using ArrayPoolSpan<int> span = new(4);
+        for (int i = 0; i < 4; i++) span[i] = i;
+
+        ReadOnlySpan<int> s = span;
+        s.Length.Should().Be(4);
+        s[0].Should().Be(0);
+        s[3].Should().Be(3);
+    }
+
+    [Test]
+    public void Enumeration_should_yield_exactly_length_elements()
+    {
+        using ArrayPoolSpan<int> span = new(5);
+        for (int i = 0; i < 5; i++) span[i] = i * 10;
+
+        int count = 0;
+        foreach (int val in span)
+        {
+            val.Should().Be(count * 10);
+            count++;
+        }
+        count.Should().Be(5);
+    }
+
+    [Test]
+    public void Slice_respects_logical_length()
+    {
+        using ArrayPoolSpan<int> span = new(5);
+        for (int i = 0; i < 5; i++) span[i] = i;
+
+        Span<int> slice = span.Slice(1, 3);
+        slice.Length.Should().Be(3);
+        slice[0].Should().Be(1);
+        slice[2].Should().Be(3);
+    }
+
+    [Test]
+    public void Slice_throws_when_exceeding_logical_length()
+    {
+        using ArrayPoolSpan<int> span = new(5);
+
+        // Start + length exceeds logical length (5), even though rented array may be larger
+        Assert.Throws<ArgumentOutOfRangeException>(() => span.Slice(3, 5));
+    }
+
+    [Test]
+    public void Slice_at_boundary_succeeds()
+    {
+        using ArrayPoolSpan<int> span = new(5);
+
+        // Exactly at the boundary should work
+        Span<int> slice = span.Slice(0, 5);
+        slice.Length.Should().Be(5);
+    }
+}
```

### src/Nethermind/Nethermind.Core/Collections/ArrayPoolSpan.cs
```diff
@@ -3,7 +3,6 @@
 
 using System.Buffers;
 using System;
-using System.Diagnostics.CodeAnalysis;
 using System.Collections.Generic;
 using System.Collections;
 
@@ -20,25 +19,19 @@ public readonly ref T this[int index]
     {
         get
         {
-            if (index > _length)
-            {
-                ThrowArgumentOutOfRangeException();
-            }
-
+            ArgumentOutOfRangeException.ThrowIfGreaterThanOrEqual(index, _length, nameof(index));
             return ref _array[index];
-
-            [DoesNotReturn]
-            static void ThrowArgumentOutOfRangeException()
-            {
-                throw new ArgumentOutOfRangeException(nameof(index));
-            }
         }
     }
 
     public static implicit operator Span<T>(ArrayPoolSpan<T> arrayPoolSpan) => arrayPoolSpan._array.AsSpan(0, arrayPoolSpan._length);
     public static implicit operator ReadOnlySpan<T>(ArrayPoolSpan<T> arrayPoolSpan) => arrayPoolSpan._array.AsSpan(0, arrayPoolSpan._length);
 
-    public Span<T> Slice(int start, int length) => _array.AsSpan(start, length);
+    public Span<T> Slice(int start, int length)
+    {
+        ArgumentOutOfRangeException.ThrowIfGreaterThan(start + length, _length, nameof(length));
+        return _array.AsSpan(start, length);
+    }
 
     public readonly void Dispose() => arrayPool.Return(_array);
 
```

### src/Nethermind/Nethermind.Network.Discovery.Test/DiscoveryMessageSerializerTests.cs
```diff
@@ -14,8 +14,10 @@
 using Nethermind.Network.Config;
 using Nethermind.Network.Discovery.Messages;
 using Nethermind.Network.Enr;
+using Nethermind.Network.Test;
 using Nethermind.Network.Test.Builders;
 using Nethermind.Stats.Model;
+using FluentAssertions;
 using Nethermind.Serialization.Rlp;
 using NUnit.Framework;
 
@@ -141,12 +143,7 @@ public void Enr_request_contains_hash()
     [Test]
     public void Enr_response_there_and_back()
     {
-        NodeRecord nodeRecord = new();
-        nodeRecord.SetEntry(new Secp256K1Entry(_privateKey.CompressedPublicKey));
-        nodeRecord.EnrSequence = 5;
-        NodeRecordSigner signer = new(new Ecdsa(), _privateKey);
-        signer.Sign(nodeRecord);
-        EnrResponseMsg msg = new(TestItem.PublicKeyA, nodeRecord, TestItem.KeccakA);
+        EnrResponseMsg msg = BuildEnrResponse(_privateKey.CompressedPublicKey);
 
         IByteBuffer serialized = _messageSerializationService.ZeroSerialize(msg);
         EnrResponseMsg deserialized = _messageSerializationService.Deserialize<EnrResponseMsg>(serialized);
@@ -156,6 +153,134 @@ public void Enr_response_there_and_back()
         Assert.That(deserialized.NodeRecord.Signature, Is.EqualTo(msg.NodeRecord.Signature));
     }
 
+    [Test]
+    public void Enr_response_deserialize_does_not_leak_buffer_on_invalid_signature()
+    {
+        // ENR with mismatched signature: Secp256K1 entry uses differentKey, but ENR is
+        // signed with _privateKey. The outer Discovery envelope is valid, but the inner
+        // ENR signature verification fails because the recovered signer doesn't match.
+        PrivateKey differentKey = new("3a1076bf45ab87712ad64ccb3b10217737f7faacbf2872e88fdd9a537d8fe266");
+        EnrResponseMsg msg = BuildEnrResponse(differentKey.CompressedPublicKey);
+        IByteBuffer serialized = _messageSerializationService.ZeroSerialize(msg);
+        int refCountBefore = serialized.ReferenceCount;
+
+        _messageSerializationService
+            .Invoking(s => s.Deserialize<EnrResponseMsg>(serialized))
+            .Should().Throw<NetworkingException>()
+            .Where(ex => ex.Message.Contains("Invalid ENR signature"));
+
+        // Buffer refcount should not have increased — no retained slices or leaked copies
+        serialized.ReferenceCount.Should().Be(refCountBefore,
+            "deserializer should not retain additional references to the buffer on error");
+        serialized.SafeRelease();
+    }
+
+    [Test]
+    public void Enr_response_deserialize_does_not_leak_buffer_on_success()
+    {
+        EnrResponseMsg msg = BuildEnrResponse(_privateKey.CompressedPublicKey);
+        IByteBuffer serialized = _messageSerializationService.ZeroSerialize(msg);
+        int refCountBefore = serialized.ReferenceCount;
+
+        EnrResponseMsg deserialized = _messageSerializationService.Deserialize<EnrResponseMsg>(serialized);
+
+        serialized.ReferenceCount.Should().Be(refCountBefore,
+            "deserializer should not retain additional references to the buffer on success");
+        deserialized.NodeRecord.EnrSequence.Should().Be(5);
+        deserialized.RequestKeccak.Should().Be(TestItem.KeccakA);
+        serialized.SafeRelease();
+    }
+
+    [Test]
+    public void Ping_deserialize_does_not_leak_buffer()
+    {
+        PingMsg msg = new(_privateKey.PublicKey, 60 + _timestamper.UnixTime.MillisecondsLong,
+            new IPEndPoint(IPAddress.Parse("192.168.1.1"), 30303),
+            new IPEndPoint(IPAddress.Parse("192.168.1.2"), 30303),
+            new byte[32])
+        {
+            FarAddress = _farAddress
+        };
+        IByteBuffer serialized = _messageSerializationService.ZeroSerialize(msg);
+        int refCountBefore = serialized.ReferenceCount;
+
+        _messageSerializationService.Deserialize<PingMsg>(serialized);
+
+        serialized.ReferenceCount.Should().Be(refCountBefore,
+            "deserializer should not retain additional references to the buffer");
+        serialized.SafeRelease();
+    }
+
+    [Test]
+    public void Pong_deserialize_does_not_leak_buffer()
+    {
+        PongMsg msg = new(_privateKey.PublicKey, 60 + _timestamper.UnixTime.MillisecondsLong, new byte[] { 1, 2, 3 })
+        {
+            FarAddress = _farAddress
+        };
+        IByteBuffer serialized = _messageSerializationService.ZeroSerialize(msg);
+        int refCountBefore = serialized.ReferenceCount;
+
+        _messageSerializationService.Deserialize<PongMsg>(serialized);
+
+        serialized.ReferenceCount.Should().Be(refCountBefore,
+            "deserializer should not retain additional references to the buffer");
+        serialized.SafeRelease();
+    }
+
+    [Test]
+    public void FindNode_deserialize_does_not_leak_buffer()
+    {
+        FindNodeMsg msg = new(_privateKey.PublicKey, 60 + _timestamper.UnixTime.MillisecondsLong, new byte[] { 1, 2, 3 })
+        {
+            FarAddress = _farAddress
+        };
+        IByteBuffer serialized = _messageSerializationService.ZeroSerialize(msg);
+        int refCountBefore = serialized.ReferenceCount;
+
+        _messageSerializationService.Deserialize<FindNodeMsg>(serialized);
+
+        serialized.ReferenceCount.Should().Be(refCountBefore,
+            "deserializer should not retain additional references to the buffer");
+        serialized.SafeRelease();
+    }
+
+    [Test]
+    public void Neighbors_deserialize_does_not_leak_buffer()
+    {
+        NeighborsMsg msg = new(_privateKey.PublicKey, 60 + _timestamper.UnixTime.MillisecondsLong,
+            new[] { new Node(TestItem.PublicKeyA, "192.168.1.2", 1) })
+        {
+            FarAddress = _farAddress
+        };
+        IByteBuffer serialized = _messageSerializationService.ZeroSerialize(msg);
+        int refCountBefore = serialized.ReferenceCount;
+
+        _messageSerializationService.Deserialize<NeighborsMsg>(serialized);
+
+        serialized.ReferenceCount.Should().Be(refCountBefore,
+            "deserializer should not retain additional references to the buffer");
+        serialized.SafeRelease();
+    }
+
+    [Test]
+    public void Neighbors_deserialize_does_not_leak_buffer_on_port_zero_rejection()
+    {
+        NeighborsMsg msg = new(_privateKey.PublicKey, 60 + _timestamper.UnixTime.MillisecondsLong,
+            new Node[] { new(TestItem.PublicKeyA, "192.168.1.2", 0) })
+        {
+            FarAddress = _farAddress
+        };
+        IByteBuffer serialized = _messageSerializationService.ZeroSerialize(msg);
+        int refCountBefore = serialized.ReferenceCount;
+
+        Assert.Throws<NetworkingException>(() => _messageSerializationService.Deserialize<NeighborsMsg>(serialized));
+
+        serialized.ReferenceCount.Should().Be(refCountBefore,
+            "deserializer should not retain additional references to the buffer on error");
+        serialized.SafeRelease();
+    }
+
     [Test]
     public void Ping_with_node_id_address_is_rejected()
     {
@@ -240,6 +365,16 @@ public void NeighborsMessageTest()
         }
     }
 
+    private EnrResponseMsg BuildEnrResponse(CompressedPublicKey enrPublicKey)
+    {
+        NodeRecord nodeRecord = new();
+        nodeRecord.SetEntry(new Secp256K1Entry(enrPublicKey));
+        nodeRecord.EnrSequence = 5;
+        NodeRecordSigner signer = new(new Ecdsa(), _privateKey);
+        signer.Sign(nodeRecord);
+        return new EnrResponseMsg(TestItem.PublicKeyA, nodeRecord, TestItem.KeccakA);
+    }
+
     [Test]
     public void NeighborsMessage_Rejects_Port_Zero()
     {
```

### src/Nethermind/Nethermind.Network.Discovery.Test/Nethermind.Network.Discovery.Test.csproj
```diff
@@ -7,6 +7,7 @@
   </PropertyGroup>
 
   <ItemGroup>
+    <PackageReference Include="FluentAssertions" />
     <PackageReference Include="Nethermind.DotNetty.Transport" />
   </ItemGroup>
 
```

### src/Nethermind/Nethermind.Network.Discovery/Serializers/EnrResponseMsgSerializer.cs
```diff
@@ -4,6 +4,7 @@
 using Autofac.Features.AttributeFilters;
 using DotNetty.Buffers;
 using Nethermind.Core.Crypto;
+using Nethermind.Core.Extensions;
 using Nethermind.Crypto;
 using Nethermind.Network.Discovery.Messages;
 using Nethermind.Network.Enr;
@@ -49,7 +50,7 @@ public EnrResponseMsg Deserialize(IByteBuffer msgBytes)
         NodeRecord nodeRecord = _nodeRecordSigner.Deserialize(ref ctx);
         if (!_nodeRecordSigner.Verify(nodeRecord))
         {
-            string resHex = data.ReadBytes(positionForHex).ReadAllHex();
+            string resHex = data.AsSpan()[..positionForHex].ToHexString();
             throw new NetworkingException($"Invalid ENR signature: {resHex}", NetworkExceptionType.Discovery);
         }
 
```

### src/Nethermind/Nethermind.Network.Test/PooledBufferLeakDetector.cs
```diff
@@ -0,0 +1,72 @@
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
+// SPDX-License-Identifier: LGPL-3.0-only
+
+using System;
+using System.Linq;
+using DotNetty.Buffers;
+using NUnit.Framework;
+
+namespace Nethermind.Network.Test;
+
+/// <summary>
+/// Detects pooled buffers that were allocated but never released back to the arena.
+/// On <see cref="Dispose"/>, asserts that the arena has zero active (unreleased) allocations.
+///
+/// Creates an isolated <see cref="PooledByteBufferAllocator"/> by default, so parallel tests
+/// do not interfere with each other. Use <see cref="Allocator"/> to obtain buffers from it.
+///
+/// <para><b>Why cache sizes must be zero:</b>
+/// DotNetty's <see cref="PooledByteBufferAllocator"/> uses thread-local caches
+/// (<c>tinyCacheSize</c>, <c>smallCacheSize</c>, <c>normalCacheSize</c>).
+/// When a buffer is released, it returns to the thread cache — not to the arena.
+/// The arena's <c>NumActiveAllocations</c> metric only decrements when a buffer is
+/// returned directly to the arena. Setting all cache sizes to <c>0</c> disables
+/// the thread-local cache so that <see cref="IByteBuffer.Release"/> goes straight
+/// to the arena, making the metric an accurate count of unreleased buffers.</para>
+///
+/// <para><b>Allocation cost:</b>
+/// Each instance creates a new <see cref="PooledByteBufferAllocator"/> with its own arena.
+/// This is acceptable for a small number of leak-detection tests, but if usage grows
+/// significantly, consider pooling and reusing allocators across tests to avoid the overhead.</para>
+///
+/// <code>
+/// using PooledBufferLeakDetector detector = new();
+/// using var input = detector.Allocator.Buffer().AsDisposable();
+/// CodeUnderTest(input);
+/// // detector.Dispose() asserts no unreleased buffers remain
+/// </code>
+/// </summary>
+public sealed class PooledBufferLeakDetector : IDisposable
+{
+    private readonly string _message;
+
+    /// <summary>
+    /// The allocator tracked by this instance. Tests should allocate buffers from this
+    /// to ensure the active-allocation count is meaningful and isolated from other tests.
+    /// </summary>
+    public PooledByteBufferAllocator Allocator { get; }
+
+    public PooledBufferLeakDetector(PooledByteBufferAllocator? allocator = null, string? message = null)
+    {
+        // Cache sizes MUST be 0 — see class doc for why.
+        Allocator = allocator ?? new PooledByteBufferAllocator(
+            nHeapArena: 1, nDirectArena: 0, pageSize: 4096, maxOrder: 0,
+            tinyCacheSize: 0, smallCacheSize: 0, normalCacheSize: 0);
+        _message = message ?? "Pooled buffer leak: buffer was allocated from the pool but never released back";
+    }
+
+    /// <summary>
+    /// Explicitly assert no leaks. Call at the end of the test body to get a clear failure
+    /// without risk of masking the original exception (as Dispose would from a finally block).
+    /// </summary>
+    public void AssertNoLeaks()
+    {
+        long active = Allocator.Metric.HeapArenas().Sum(a => a.NumActiveAllocations);
+        Assert.That(active, Is.EqualTo(0), _message);
+    }
+
+    public void Dispose()
+    {
+        AssertNoLeaks();
+    }
+}
```

### src/Nethermind/Nethermind.Network.Test/Rlpx/SnappyTests.cs
```diff
@@ -112,27 +112,18 @@ public void Roundtrip_zero()
     [Test]
     public void Encode_does_not_leak_pooled_buffers()
     {
-        PooledByteBufferAllocator allocator = new(
-            nHeapArena: 1, nDirectArena: 0, pageSize: 4096, maxOrder: 0);
+        using PooledBufferLeakDetector detector = new();
         ZeroSnappyEncoderForTest encoder = new();
 
         // RLP-encoded packet type (0x01) followed by an RLP-encoded body
         byte[] packetType = Rlp.Encode(1).Bytes;
         byte[] body = Rlp.Encode(new byte[100]).Bytes;
         byte[] payload = Bytes.Concat(packetType, body);
-        using DisposableByteBuffer input = allocator.Buffer().AsDisposable();
-        using DisposableByteBuffer output = allocator.Buffer().AsDisposable();
+        using DisposableByteBuffer input = detector.Allocator.Buffer().AsDisposable();
+        using DisposableByteBuffer output = detector.Allocator.Buffer().AsDisposable();
 
         input.WriteBytes(payload);
 
-        long activeBefore = allocator.Metric.HeapArenas().Sum(a => a.NumActiveAllocations);
-
         encoder.TestEncode(input, output);
-
-        long activeAfter = allocator.Metric.HeapArenas().Sum(a => a.NumActiveAllocations);
-
-        // No new active allocations should remain after Encode — any intermediate
-        // buffer must be released. A leak causes activeAfter > activeBefore.
-        Assert.That(activeAfter, Is.EqualTo(activeBefore));
     }
 }
```
