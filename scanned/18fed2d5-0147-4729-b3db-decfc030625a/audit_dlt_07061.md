# [?] Fix RLPx/Snappy frame decoding correctness and DoS issues (#12896)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-08-27
Source: https://github.com/NethermindEth/nethermind/commit/8476e9f4339af4f3765e84ded7bf5e6aebe10247
Type: security-commit

## Details
Fix RLPx/Snappy frame decoding correctness and DoS issues (#12896)

* Fix RLPx/Snappy frame decoding correctness and DoS issues

- Reject malformed RLPx header bodies whose claimed RLP length exceeds the
  13-byte header body, wrapping RLP exceptions as CorruptedFrameException.
- Reject continuation frames larger than the remaining packet size and release
  the in-progress packet on failure.
- Convert Snappy decompression failures (InvalidDataException) to
  CorruptedFrameException in both SnappyDecoder and ZeroNettyP2PHandler; log a
  hex prefix of the offending payload.
- Reject packet type prefixes whose decoded length exceeds the remaining buffer
  in ZeroSnappyEncoder.
- Reject packet type prefixes whose decoded length exceeds the frame payload
  size in ZeroFrameMerger.
- Add regression tests for all cases.

* Address review feedback on RLPx frame decoding hardening

Fix the Snappy failure log emitting at Error severity behind an IsDebug guard,
bound the decompression output span by the declared uncompressed length, keep
the RLP exception handling out of the inlined first-chunk path, scope the frame
header try/catch to the RLP decoding only, and compare the frame context id
against the previous one before overwriting it so a frame from another
multiplexed stream is no longer merged into the packet in progress.

The outbound encoder guard now throws InvalidOperationException instead of the
inbound-only CorruptedFrameException, which would blame the peer for a local
bug.

* Reject RLPx packet types that do not fit in a byte

A peer could send an RLP packet type above 255 - for example 256 - and have it
truncated by the cast to byte, silently delivering the frame as a different
message. Reject it in the same place the packet type prefix length is checked.

Also add the positive counterpart of the context id test: a frame carrying a
non-zero context id with no packet in progress is a normal frame and must be
accepted, and assert the inbound packet is released when Snappy decoding throws.

* Use the pooled buffer leak detector for frame merger release assertions

Replaces the NSubstitute allocator stub and its AllocatedBuffer property with
PooledBufferLeakDetector, which the test infrastructure rules point at for this
exact case. The substitute returned null for every allocator member other than
Buffer(int), which would have turned any future call into an opaque NRE.

Also correct the ReadHeaderBody remark - the catch filter never could have
caught a CorruptedFrameException, so the split is about scoping the region to
the RLP decoding, not about swallowing - and report the real remaining byte
count in the header length message instead of the full header body size.

* Harden RLPx frame and Snappy validation

* Harden RLPx malformed frame handling

## Patch
### src/Nethermind/Nethermind.Network.Test/Rlpx/FrameHeaderReaderTests.cs
```diff
@@ -1,4 +1,4 @@
-// SPDX-FileCopyrightText: 2025 Demerzel Solutions Limited
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using System.Collections.Generic;
@@ -61,5 +61,34 @@ private static IEnumerable<TestCaseData> TotalPacketSizeExceedsLimitInvalidCases
             yield return new(200, 100L) { TestName = "Frame_size_cannot_exceed_total_size", ExpectedResult = false };
             yield return new(1, (long)uint.MaxValue) { TestName = "Total_size_cannot_be_negative", ExpectedResult = false };
         }
+
+        [Test]
+        [TestCaseSource(nameof(MalformedHeaderBodyPrefixes))]
+        public void Throws_corrupted_frame_when_rlp_header_body_is_malformed(byte[] headerBodyPrefix)
+        {
+            FrameHeaderReader reader = new();
+            using DisposableByteBuffer buffer = Unpooled.Buffer(Frame.HeaderSize).AsDisposable();
+
+            const int frameSize = 1;
+            buffer.WriteByte(frameSize >> 16);
+            buffer.WriteByte(frameSize >> 8);
+            buffer.WriteByte(frameSize);
+
+            buffer.WriteBytes(headerBodyPrefix);
+            buffer.WriteZero(Frame.HeaderSize - buffer.WriterIndex);
+
+            Assert.That(() => reader.ReadFrameHeader(buffer),
+                Throws.InstanceOf<CorruptedFrameException>(),
+                "malformed header body RLP must be rejected as corrupted frame");
+        }
+
+        private static IEnumerable<TestCaseData> MalformedHeaderBodyPrefixes()
+        {
+            yield return new TestCaseData(new byte[] { 0xf7 }).SetName("Short_list_length_exceeds_available_header_body");
+            yield return new TestCaseData(new byte[] { 0xf8, 0x00 }).SetName("Long_list_uses_non_canonical_zero_length");
+            yield return new TestCaseData(new byte[] { 0xf8, 0x38 }).SetName("Long_list_length_exceeds_available_header_body");
+            yield return new TestCaseData(new byte[] { 0xfb, 0xff, 0xff, 0xff, 0xff }).SetName("Long_list_length_overflows_int");
+            yield return new TestCaseData(new byte[] { 0xff }).SetName("Long_list_length_of_length_exceeds_supported_width");
+        }
     }
 }
```

### src/Nethermind/Nethermind.Network.Test/Rlpx/SnappyTests.cs
```diff
@@ -1,38 +1,27 @@
-// SPDX-FileCopyrightText: 2022 Demerzel Solutions Limited
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
 // SPDX-License-Identifier: LGPL-3.0-only
 
-using System.Collections.Generic;
 using System.IO;
 using System.Linq;
 using DotNetty.Buffers;
+using DotNetty.Transport.Channels;
 using Nethermind.Core;
 using Nethermind.Core.Extensions;
 using Nethermind.Logging;
+using Nethermind.Network.P2P;
+using Nethermind.Network.P2P.ProtocolHandlers;
 using Nethermind.Network.Rlpx;
 using Nethermind.Serialization.Rlp;
+using NSubstitute;
 using NUnit.Framework;
+using Snappier;
 
 namespace Nethermind.Network.Test.Rlpx;
 
 public class SnappyTests
 {
     private readonly string _uncompressedTestFileName = Path.Combine(TestContext.CurrentContext.WorkDirectory, "Rlpx", "block.rlp");
 
-    public class SnappyDecoderForTest : SnappyDecoder
-    {
-        public SnappyDecoderForTest()
-            : base(LimboTraceLogger.Instance)
-        {
-        }
-
-        public byte[] TestDecode(byte[] input)
-        {
-            List<object> result = [];
-            Decode(null, new Packet(input), result);
-            return ((Packet)result[0]).Data;
-        }
-    }
-
     public class ZeroSnappyEncoderForTest : ZeroSnappyEncoder
     {
         public ZeroSnappyEncoderForTest()
@@ -50,17 +39,6 @@ public byte[] TestEncode(byte[] input)
         public void TestEncode(IByteBuffer input, IByteBuffer output) => Encode(null, input, output);
     }
 
-    [TestCase("block.go.snappy")]
-    [TestCase("block.py.snappy")]
-    public void Can_decompress_compressed_file(string compressedFileName)
-    {
-        SnappyDecoderForTest decoder = new();
-        byte[] expectedUncompressed = Bytes.FromHexString(File.ReadAllText(Path.Combine(TestContext.CurrentContext.WorkDirectory, "Rlpx", _uncompressedTestFileName)));
-        byte[] compressed = Bytes.FromHexString(File.ReadAllText(Path.Combine(TestContext.CurrentContext.WorkDirectory, "Rlpx", compressedFileName)));
-        byte[] uncompressedResult = decoder.TestDecode(compressed);
-        Assert.That(uncompressedResult, Is.EqualTo(expectedUncompressed));
-    }
-
     [Test]
     public void Can_load_block_rlp_test_file()
     {
@@ -76,14 +54,61 @@ public void Can_load_compressed_test_file(string compressedFileName)
         Assert.That(bytes.Length, Is.GreaterThan(70 * MemorySizes.KiB));
     }
 
+    [TestCase("block.go.snappy")]
+    [TestCase("block.py.snappy")]
+    public void Zero_netty_p2p_handler_can_decompress_compressed_file(string compressedFileName)
+    {
+        const byte packetType = 0x05;
+        byte[] expectedUncompressed = Bytes.FromHexString(File.ReadAllText(_uncompressedTestFileName));
+        byte[] compressed = Bytes.FromHexString(File.ReadAllText(Path.Combine(TestContext.CurrentContext.WorkDirectory, "Rlpx", compressedFileName)));
+
+        ISession session = Substitute.For<ISession>();
+        IChannelHandlerContext context = Substitute.For<IChannelHandlerContext>();
+        context.Allocator.Returns(UnpooledByteBufferAllocator.Default);
+
+        ZeroPacket received = null;
+        session.When(static s => s.ReceiveMessage(Arg.Any<ZeroPacket>()))
+            .Do(call =>
+            {
+                received = call.Arg<ZeroPacket>();
+                received.Retain();
+            });
+
+        IByteBuffer content = Unpooled.Buffer(compressed.Length);
+        content.WriteBytes(compressed);
+        ZeroPacket packet = new(content)
+        {
+            PacketType = packetType
+        };
+
+        ZeroNettyP2PHandler handler = new(session, LimboLogs.Instance);
+        handler.EnableSnappy();
+
+        try
+        {
+            handler.ChannelRead(context, packet);
+
+            Assert.That(received, Is.Not.Null);
+            using (Assert.EnterMultipleScope())
+            {
+                Assert.That(received.PacketType, Is.EqualTo(packetType));
+                Assert.That(received.Content.ReadAllBytesAsArray(), Is.EqualTo(expectedUncompressed));
+            }
+        }
+        finally
+        {
+            received?.Release();
+        }
+    }
+
     [Test]
     [Ignore("Needs further investigation. For now ignoring as it would be requiring too much time.")]
     public void Uses_same_compression_as_py_zero_or_go()
     {
         string rlpxDir = Path.Combine(TestContext.CurrentContext.WorkDirectory, "Rlpx");
         byte[] bytesPy = Bytes.FromHexString(File.ReadAllText(Path.Combine(rlpxDir, "block.py.snappy")));
         byte[] bytesGo = Bytes.FromHexString(File.ReadAllText(Path.Combine(rlpxDir, "block.go.snappy")));
-        byte[] bytesUncompressed = Bytes.FromHexString(File.ReadAllText(Path.Combine(rlpxDir, _uncompressedTestFileName)));
+        byte[] bytesUncompressed = Bytes.FromHexString(File.ReadAllText(_uncompressedTestFileName));
 
         ZeroSnappyEncoderForTest encoder = new();
         byte[] compressed = encoder.TestEncode(Bytes.Concat(1, bytesUncompressed));
@@ -94,11 +119,10 @@ public void Uses_same_compression_as_py_zero_or_go()
     [Test]
     public void Roundtrip_zero()
     {
-        SnappyDecoderForTest decoder = new();
         ZeroSnappyEncoderForTest encoder = new();
-        byte[] expectedUncompressed = Bytes.FromHexString(File.ReadAllText(Path.Combine(TestContext.CurrentContext.WorkDirectory, "Rlpx", _uncompressedTestFileName)));
+        byte[] expectedUncompressed = Bytes.FromHexString(File.ReadAllText(_uncompressedTestFileName));
         byte[] compressed = encoder.TestEncode(Bytes.Concat(1, expectedUncompressed));
-        byte[] uncompressedResult = decoder.TestDecode(compressed.Skip(1).ToArray());
+        byte[] uncompressedResult = Snappy.DecompressToArray(compressed.Skip(1).ToArray());
         Assert.That(uncompressedResult, Is.EqualTo(expectedUncompressed));
     }
 
```

### src/Nethermind/Nethermind.Network.Test/Rlpx/TestWrappers/ZeroFrameMergerTestWrapper.cs
```diff
@@ -12,11 +12,15 @@ namespace Nethermind.Network.Test.Rlpx.TestWrappers
 {
     internal class ZeroFrameMergerTestWrapper : ZeroFrameMerger
     {
-        public ZeroFrameMergerTestWrapper()
-            : base(LimboLogs.Instance) => _context.Allocator.Returns(UnpooledByteBufferAllocator.Default);
-
         private readonly IChannelHandlerContext _context = Substitute.For<IChannelHandlerContext>();
 
+        /// <param name="allocator">
+        /// Allocator the merger draws in-progress packet buffers from. Pass a <see cref="PooledBufferLeakDetector"/>
+        /// allocator to assert those buffers are released.
+        /// </param>
+        public ZeroFrameMergerTestWrapper(IByteBufferAllocator? allocator = null)
+            : base(LimboLogs.Instance) => _context.Allocator.Returns(allocator ?? UnpooledByteBufferAllocator.Default);
+
         public ZeroPacket Decode(IByteBuffer input)
         {
             List<object> result = [];
```

### src/Nethermind/Nethermind.Network.Test/Rlpx/ZeroNettyFrameMergerTests.cs
```diff
@@ -1,10 +1,14 @@
-// SPDX-FileCopyrightText: 2022 Demerzel Solutions Limited
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
 // SPDX-License-Identifier: LGPL-3.0-only
 
+using System.Collections.Generic;
+using System.Linq;
 using DotNetty.Buffers;
 using DotNetty.Codecs;
 using DotNetty.Transport.Channels;
+using DotNetty.Transport.Channels.Embedded;
 using Nethermind.Core.Extensions;
+using Nethermind.Logging;
 using Nethermind.Network.P2P.Messages;
 using Nethermind.Network.Rlpx;
 using Nethermind.Network.Test.Rlpx.TestWrappers;
@@ -27,6 +31,9 @@ public TestFrameHelper() : base()
         }
     }
 
+    /// <summary>Byte offset of the context id within a frame header: 3 size bytes, the RLP list prefix, the capability id.</summary>
+    private const int ContextIdOffsetInHeader = 5;
+
     private static IByteBuffer BuildFrames(int count)
     {
         TestFrameHelper frameBuilder = new();
@@ -40,6 +47,36 @@ private static IByteBuffer BuildFrames(int count)
         return output;
     }
 
+    private static IByteBuffer BuildFrame(byte[] payload, int contextId, int? totalPacketSize = null)
+    {
+        int paddingSize = Frame.CalculatePadding(payload.Length);
+        IByteBuffer output = PooledByteBufferAllocator.Default.Buffer(Frame.HeaderSize + payload.Length + paddingSize);
+
+        output.WriteByte(payload.Length >> 16);
+        output.WriteByte(payload.Length >> 8);
+        output.WriteByte(payload.Length);
+
+        int headerContentLength = Rlp.LengthOf(0) + Rlp.LengthOf(contextId);
+        if (totalPacketSize.HasValue)
+        {
+            headerContentLength += Rlp.LengthOf(totalPacketSize.Value);
+        }
+
+        ByteBufferRlpWriter writer = new(output);
+        writer.StartSequence(headerContentLength);
+        writer.Encode(0);
+        writer.Encode(contextId);
+        if (totalPacketSize.HasValue)
+        {
+            writer.Encode(totalPacketSize.Value);
+        }
+
+        output.WriteZero(Frame.HeaderSize - output.WriterIndex);
+        output.WriteBytes(payload);
+        output.WriteZero(paddingSize);
+        return output;
+    }
+
     [Test]
     public void Handles_non_chunked_frames()
     {
@@ -183,33 +220,264 @@ public void Can_merge_big_frame()
     }
 
     [Test]
-    public void Throws_on_continuation_frame_with_no_in_progress_packet()
+    public void Allocates_only_the_received_chunk_while_packet_is_in_progress()
     {
-        ZeroFrameMergerTestWrapper wrapper = new();
+        int totalPacketSize = (int)1.MiB;
+        IByteBufferAllocator allocator = Substitute.For<IByteBufferAllocator>();
+        allocator.Buffer(Arg.Any<int>()).Returns(call => UnpooledByteBufferAllocator.Default.Buffer(call.Arg<int>()));
+        allocator.Buffer(Arg.Any<int>(), Arg.Any<int>()).Returns(call =>
+            UnpooledByteBufferAllocator.Default.Buffer(call.ArgAt<int>(0), call.ArgAt<int>(1)));
+        ZeroFrameMergerTestWrapper wrapper = new(allocator);
+
+        try
+        {
+            byte[] firstPayload = new byte[Frame.BlockSize];
+            firstPayload[0] = 2;
+            using DisposableByteBuffer firstFrame = BuildFrame(firstPayload, contextId: 1, totalPacketSize: totalPacketSize).AsDisposable();
+            ZeroPacket packet = wrapper.Decode(firstFrame);
+            Assert.That(packet, Is.Null, "the first frame must not complete the declared packet");
+
+            allocator.Received(1).Buffer(Frame.BlockSize - 1, totalPacketSize - 1);
+        }
+        finally
+        {
+            wrapper.HandlerRemoved(Substitute.For<IChannelHandlerContext>());
+        }
+    }
+
+    [Test]
+    public void Releases_and_recovers_when_continuation_header_is_malformed()
+    {
+        using PooledBufferLeakDetector detector = new();
+        ZeroFrameMergerTestWrapper wrapper = new(detector.Allocator);
+        long initialActiveAllocations = detector.Allocator.Metric.HeapArenas().Sum(static arena => arena.NumActiveAllocations);
+
+        using DisposableByteBuffer frames = BuildFrames(2).AsDisposable();
+        const int firstFrameLength = Frame.HeaderSize + Frame.DefaultMaxFrameSize;
+        using DisposableByteBuffer firstFrame = PooledByteBufferAllocator.Default.Buffer(firstFrameLength).AsDisposable();
+        firstFrame.WriteBytes(frames, frames.ReaderIndex, firstFrameLength);
+        Assert.That(wrapper.Decode(firstFrame), Is.Null, "the first frame must leave a packet in progress");
+
+        using DisposableByteBuffer malformedHeader = Unpooled.Buffer(Frame.HeaderSize).AsDisposable();
+        malformedHeader.WriteByte(0);
+        malformedHeader.WriteByte(0);
+        malformedHeader.WriteByte(1);
+        malformedHeader.WriteByte(0xf7);
+        malformedHeader.WriteZero(Frame.HeaderSize - malformedHeader.WriterIndex);
+
+        Assert.That(() => wrapper.Decode(malformedHeader), Throws.InstanceOf<CorruptedFrameException>());
+        long activeAllocations = detector.Allocator.Metric.HeapArenas().Sum(static arena => arena.NumActiveAllocations);
+        Assert.That(activeAllocations, Is.EqualTo(initialActiveAllocations),
+            "a malformed continuation header must release the in-progress packet immediately");
 
-        using DisposableByteBuffer firstPacket = BuildFrames(3).AsDisposable();
-        ZeroPacket completed = null;
+        using DisposableByteBuffer recoveryInput = BuildFrames(1).AsDisposable();
+        ZeroPacket recovered = wrapper.Decode(recoveryInput);
         try
         {
-            completed = wrapper.Decode(firstPacket);
-            Assert.That(completed, Is.Not.Null);
+            Assert.That(recovered, Is.Not.Null, "the merger must accept a fresh packet after the malformed header");
+        }
+        finally
+        {
+            recovered?.Release();
+        }
+    }
 
-            using DisposableByteBuffer orphanSource = BuildFrames(3).AsDisposable();
-            const int firstFrameSize = Frame.HeaderSize + Frame.DefaultMaxFrameSize;
-            const int continuationFrameOffset = firstFrameSize;
-            using DisposableByteBuffer orphanFrame = PooledByteBufferAllocator.Default.Buffer(firstFrameSize).AsDisposable();
-            orphanFrame.WriteBytes(orphanSource, srcIndex: continuationFrameOffset, length: firstFrameSize);
+    [Test]
+    public void Drains_full_frame_and_recovers_when_continuation_header_is_malformed()
+    {
+        EmbeddedChannel channel = new();
+        channel.Pipeline.AddLast(new ZeroFrameMerger(LimboLogs.Instance));
 
-            Assert.That(() => wrapper.Decode(orphanFrame),
+        try
+        {
+            using DisposableByteBuffer frames = BuildFrames(2).AsDisposable();
+            const int firstFrameLength = Frame.HeaderSize + Frame.DefaultMaxFrameSize;
+            Assert.That(channel.WriteInbound(frames.ReadRetainedSlice(firstFrameLength)), Is.False,
+                "the first frame must leave a packet in progress");
+
+            IByteBuffer malformedFrame = BuildFrame([0], contextId: 1);
+            malformedFrame.SetByte(3, 0xf7);
+
+            Assert.That(() => channel.WriteInbound(malformedFrame),
                 Throws.InstanceOf<CorruptedFrameException>(),
-                "continuation frame without an in-progress packet must be rejected");
+                "a malformed continuation header must reject the entire decoded frame");
+
+            IByteBuffer recoveryFrame = BuildFrames(1);
+            Assert.That(channel.WriteInbound(recoveryFrame), Is.True,
+                "the merger must not retain payload or padding from the rejected frame");
+
+            ZeroPacket recovered = channel.ReadInbound<ZeroPacket>();
+            try
+            {
+                Assert.That(recovered, Is.Not.Null);
+            }
+            finally
+            {
+                recovered?.Release();
+            }
         }
         finally
         {
-            completed?.Release();
+            channel.FinishAndReleaseAll();
         }
     }
 
+    [Test]
+    public void Throws_when_continuation_frame_exceeds_remaining_packet_size()
+    {
+        using PooledBufferLeakDetector detector = new(message: "the in-progress packet buffer must be released, not just dropped");
+        ZeroFrameMergerTestWrapper wrapper = new(detector.Allocator);
+
+        // Build a valid two-frame packet and then corrupt the continuation frame's size field.
+        using DisposableByteBuffer frames = BuildFrames(2).AsDisposable();
+
+        // Locate the second frame. First frame payload = Frame.DefaultMaxFrameSize (1024), padding = 0.
+        int firstFrameLength = Frame.HeaderSize + Frame.DefaultMaxFrameSize;
+        int secondFrameOffset = firstFrameLength;
+
+        // The second frame originally has payload size 2. Tamper with its 3-byte size
+        // field to claim 100 payload bytes, which exceeds the remaining packet size.
+        const int tamperedSecondFrameSize = 100;
+        frames.SetByte(secondFrameOffset, tamperedSecondFrameSize >> 16);
+        frames.SetByte(secondFrameOffset + 1, tamperedSecondFrameSize >> 8);
+        frames.SetByte(secondFrameOffset + 2, tamperedSecondFrameSize);
+
+        using DisposableByteBuffer firstFrame = PooledByteBufferAllocator.Default.Buffer(firstFrameLength).AsDisposable();
+        firstFrame.WriteBytes(frames, frames.ReaderIndex, firstFrameLength);
+        ZeroPacket completed = wrapper.Decode(firstFrame);
+        Assert.That(completed, Is.Null, "first frame alone should not complete a packet");
+
+        int secondFrameLength = Frame.HeaderSize + tamperedSecondFrameSize + Frame.CalculatePadding(tamperedSecondFrameSize);
+        using DisposableByteBuffer continuationFrame = PooledByteBufferAllocator.Default.Buffer(secondFrameLength).AsDisposable();
+        continuationFrame.WriteBytes(frames, secondFrameOffset, Frame.HeaderSize);
+        continuationFrame.WriteZero(tamperedSecondFrameSize);
+        continuationFrame.WriteZero(Frame.CalculatePadding(tamperedSecondFrameSize));
+
+        Assert.That(() => wrapper.Decode(continuationFrame),
+            Throws.InstanceOf<CorruptedFrameException>(),
+            "continuation frame larger than remaining packet size must be rejected");
+
+        using DisposableByteBuffer recoveryInput = BuildFrames(1).AsDisposable();
+        ZeroPacket recovered = wrapper.Decode(recoveryInput);
+        try
+        {
+            Assert.That(recovered, Is.Not.Null, "merger must accept a fresh packet after recovery from the throw");
+        }
+        finally
+        {
+            recovered?.Release();
+        }
+    }
+
+    [TestCase(false, TestName = "Merges_normal_frame_with_context_id_on_fresh_connection")]
+    [TestCase(true, TestName = "Merges_normal_frame_reusing_completed_context_id")]
+    public void Merges_normal_frame_with_context_id_when_no_packet_is_in_progress(bool completeChunkedPacketFirst)
+    {
+        ZeroFrameMergerTestWrapper wrapper = new();
+
+        if (completeChunkedPacketFirst)
+        {
+            using DisposableByteBuffer chunkedFrames = BuildFrames(2).AsDisposable();
+            ZeroPacket completedPacket = wrapper.Decode(chunkedFrames);
+            try
+            {
+                Assert.That(completedPacket, Is.Not.Null);
+            }
+            finally
+            {
+                completedPacket?.Release();
+            }
+        }
+
+        using DisposableByteBuffer frame = BuildFrames(1).AsDisposable();
+
+        // The splitter emits [capability id, context id] = [0, 0] for a single frame; a non-zero context id with no
+        // total packet size is still a normal frame as long as no packet is open under it.
+        frame.SetByte(ContextIdOffsetInHeader, 1);
+
+        ZeroPacket packet = wrapper.Decode(frame);
+        try
+        {
+            Assert.That(packet, Is.Not.Null, "a frame carrying a context id must not be mistaken for a continuation");
+        }
+        finally
+        {
+            packet?.Release();
+        }
+    }
+
+    [Test]
+    public void Merges_chunked_packet_when_intermediate_frame_has_padding()
+    {
+        ZeroFrameMergerTestWrapper wrapper = new();
+
+        using DisposableByteBuffer firstFrame = BuildFrame([2, 0, 0, 0, 0], contextId: 1, totalPacketSize: 7).AsDisposable();
+        Assert.That(wrapper.Decode(firstFrame), Is.Null, "the first chunk must leave the packet open");
+
+        using DisposableByteBuffer finalFrame = BuildFrame([0, 0], contextId: 1).AsDisposable();
+        ZeroPacket packet = wrapper.Decode(finalFrame);
+        try
+        {
+            Assert.That(packet, Is.Not.Null);
+            Assert.That(packet.Content.ReadableBytes, Is.EqualTo(6));
+        }
+        finally
+        {
+            packet?.Release();
+        }
+    }
+
+    [Test]
+    public void Throws_when_continuation_frame_carries_a_different_context_id()
+    {
+        using PooledBufferLeakDetector detector = new(message: "the in-progress packet buffer must be released, not just dropped");
+        ZeroFrameMergerTestWrapper wrapper = new(detector.Allocator);
+
+        using DisposableByteBuffer frames = BuildFrames(2).AsDisposable();
+
+        // Bumping the context id detaches the continuation frame from the packet opened by the frame above it.
+        const int continuationContextIdOffset = Frame.HeaderSize + Frame.DefaultMaxFrameSize + ContextIdOffsetInHeader;
+        frames.SetByte(continuationContextIdOffset, frames.GetByte(continuationContextIdOffset) + 1);
+
+        Assert.That(() => wrapper.Decode(frames),
+            Throws.InstanceOf<CorruptedFrameException>(),
+            "a frame from another context id must not be merged into the in-progress packet");
+    }
+
+    [Test]
+    [TestCaseSource(nameof(MalformedPacketTypePayloads))]
+    public void Throws_when_packet_type_prefix_is_invalid_or_exceeds_frame_size(byte[] payloadPrefix, int frameSize)
+    {
+        ZeroFrameMergerTestWrapper wrapper = new();
+
+        int paddingSize = Frame.CalculatePadding(frameSize);
+        using DisposableByteBuffer frame = PooledByteBufferAllocator.Default.Buffer(Frame.HeaderSize + frameSize + paddingSize).AsDisposable();
+
+        frame.WriteByte(frameSize >> 16);
+        frame.WriteByte(frameSize >> 8);
+        frame.WriteByte(frameSize);
+
+        frame.WriteByte(0xc2);
+        frame.WriteByte(0x80);
+        frame.WriteByte(0x80);
+        frame.WriteZero(Frame.HeaderSize - frame.WriterIndex);
+
+        frame.WriteBytes(payloadPrefix);
+        frame.WriteZero(frameSize - payloadPrefix.Length + paddingSize);
+
+        Assert.That(() => wrapper.Decode(frame),
+            Throws.InstanceOf<CorruptedFrameException>(),
+            "malformed packet type RLP must be rejected as corrupted frame");
+    }
+
+    private static IEnumerable<TestCaseData> MalformedPacketTypePayloads()
+    {
+        yield return new TestCaseData(new byte[] { 0x85, 0x01 }, 5).SetName("Packet_type_length_exceeds_frame_size");
+        yield return new TestCaseData(new byte[] { 0xb8, 0x38 }, 5).SetName("Packet_type_integer_length_exceeds_supported_width");
+        // 256 would otherwise be truncated to 0 and delivered as a Hello.
+        yield return new TestCaseData(new byte[] { 0x82, 0x01, 0x00 }, 5).SetName("Packet_type_value_does_not_fit_in_a_byte");
+    }
+
     [Test]
     public void Throws_and_recovers_when_new_first_chunk_arrives_before_previous_completes()
     {
```

### src/Nethermind/Nethermind.Network.Test/Rlpx/ZeroNettyP2PHandlerTests.cs
```diff
@@ -1,37 +1,66 @@
-// SPDX-FileCopyrightText: 2022 Demerzel Solutions Limited
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using System;
+using System.Collections.Generic;
+using System.Linq;
 using System.Threading.Tasks;
 using DotNetty.Buffers;
+using DotNetty.Codecs;
 using DotNetty.Transport.Channels;
 using Nethermind.Core.Exceptions;
-using Nethermind.Core.Extensions;
+using Nethermind.Core.Test.Builders;
 using Nethermind.Logging;
 using Nethermind.Network.P2P;
 using Nethermind.Network.P2P.ProtocolHandlers;
 using Nethermind.Network.Rlpx;
-using Nethermind.Serialization.Rlp;
 using Nethermind.Stats.Model;
 using NSubstitute;
 using NUnit.Framework;
 using Snappier;
-using System.Linq;
 
 namespace Nethermind.Network.Test.Rlpx;
 
 public class ZeroNettyP2PHandlerTests
 {
     [Test]
-    public void When_exception_is_thrown_send_disconnect_message()
+    [TestCaseSource(nameof(ExceptionDisconnectCases))]
+    public void When_exception_is_thrown_send_disconnect_message(Exception exception, DisconnectReason expectedReason)
+    {
+        ISession session = Substitute.For<ISession>();
+        IChannelHandlerContext channelHandlerContext = Substitute.For<IChannelHandlerContext>();
+        ZeroNettyP2PHandler handler = new(session, LimboLogs.Instance);
+
+        handler.ExceptionCaught(channelHandlerContext, exception);
+
+        session.Received().InitiateDisconnect(expectedReason, Arg.Any<string>());
+    }
+
+    private static IEnumerable<TestCaseData> ExceptionDisconnectCases()
+    {
+        yield return new TestCaseData(new Exception(), DisconnectReason.Exception).SetName("Generic_exception_uses_generic_reason");
+        yield return new TestCaseData(new CorruptedFrameException("malformed frame"), DisconnectReason.Exception).SetName("Corrupted_frame_uses_generic_reason");
+    }
+
+    [TestCase(true)]
+    [TestCase(false)]
+    public void When_corrupted_frame_is_received_from_privileged_peer_then_keep_session(bool isStatic)
     {
+        Node node = new(TestItem.PublicKeyA, "127.0.0.1", 30303)
+        {
+            IsStatic = isStatic,
+            IsTrusted = !isStatic
+        };
         ISession session = Substitute.For<ISession>();
+        session.Node.Returns(node);
         IChannelHandlerContext channelHandlerContext = Substitute.For<IChannelHandlerContext>();
         ZeroNettyP2PHandler handler = new(session, LimboLogs.Instance);
+        CorruptedFrameException exception = new("malformed frame");
 
-        handler.ExceptionCaught(channelHandlerContext, new Exception());
+        handler.ExceptionCaught(channelHandlerContext, exception);
 
-        session.Received().InitiateDisconnect(Arg.Any<DisconnectReason>(), Arg.Any<string>());
+        session.DidNotReceive().InitiateDisconnect(Arg.Any<DisconnectReason>(), Arg.Any<string>());
+        channelHandlerContext.Received().FireExceptionCaught(exception);
     }
 
     [Test]
@@ -46,57 +75,70 @@ public async Task When_internal_nethermind_exception_is_thrown__then_do_not_disc
         await channelHandlerContext.DidNotReceive().DisconnectAsync();
     }
 
-
     [Test]
-    public void When_not_a_snappy_encoded_data_then_pass_data_directly()
+    [TestCaseSource(nameof(MalformedSnappyPayloads))]
+    public void When_malformed_snappy_data_then_throw_corrupted_frame(byte[] msg)
     {
+        IByteBufferAllocator allocator = Substitute.For<IByteBufferAllocator>();
         IChannelHandlerContext channelHandlerContext = Substitute.For<IChannelHandlerContext>();
-        channelHandlerContext.Allocator.Returns(UnpooledByteBufferAllocator.Default);
-
-        byte[] msg = Bytes.FromHexString("0x10");
+        channelHandlerContext.Allocator.Returns(allocator);
 
         ISession session = Substitute.For<ISession>();
-        session.When(s => s.ReceiveMessage(Arg.Any<ZeroPacket>()))
-            .Do(c =>
-            {
-                ZeroPacket packet = (ZeroPacket)c[0];
-                Assert.That(packet.Content.ReadAllBytesAsArray(), Is.EqualTo(msg));
-            });
-
         ZeroNettyP2PHandler handler = new(session, LimboLogs.Instance);
         handler.EnableSnappy();
 
         IByteBuffer buff = Unpooled.Buffer(2);
         buff.WriteBytes(msg);
         ZeroPacket packet = new(buff);
 
-        handler.ChannelRead(channelHandlerContext, packet); // releases buffer
+        Assert.That(() => handler.ChannelRead(channelHandlerContext, packet), Throws.InstanceOf<CorruptedFrameException>());
+
+        session.DidNotReceive().ReceiveMessage(Arg.Any<ZeroPacket>());
+        allocator.DidNotReceive().Buffer(Arg.Any<int>());
+        Assert.That(packet.ReferenceCount, Is.Zero, "the inbound packet must be released even when decoding throws");
+    }
+
+    private static IEnumerable<TestCaseData> MalformedSnappyPayloads()
+    {
+        yield return new TestCaseData(new byte[] { 0x80 }).SetName("Invalid_length_varint");
+        yield return new TestCaseData(new byte[] { 0x01 }).SetName("Missing_literal_data");
+        yield return new TestCaseData(new byte[] { 0x01, 0x04, 0x41, 0x42 }).SetName("Literal_exceeds_declared_length");
+        yield return new TestCaseData(new byte[] { 0x01, 0x00, 0x41, 0x01 }).SetName("Incomplete_tag_after_declared_length");
+        yield return new TestCaseData(new byte[] { 0x00, 0x00 }).SetName("Suffix_after_zero_length_block");
+        yield return new TestCaseData(new byte[] { 0x80, 0x80, 0x80, 0x08 }).SetName("Declared_length_cannot_be_represented_by_payload");
+        // A frame sized exactly to its packet type prefix leaves no content bytes at all.
+        yield return new TestCaseData(Array.Empty<byte>()).SetName("Empty_payload");
     }
 
     [Test]
-    public void When_message_exceeds_max_size_then_disconnect_with_breach_of_protocol()
+    [TestCaseSource(nameof(SnappyPayloadsExceedingMaxLength))]
+    public void When_message_exceeds_max_size_then_disconnect_with_breach_of_protocol(byte[] data)
     {
-        // Arrange
+        IByteBufferAllocator allocator = Substitute.For<IByteBufferAllocator>();
         ISession session = Substitute.For<ISession>();
         IChannelHandlerContext channelHandlerContext = Substitute.For<IChannelHandlerContext>();
-        channelHandlerContext.Allocator.Returns(UnpooledByteBufferAllocator.Default);
+        channelHandlerContext.Allocator.Returns(allocator);
 
         ZeroNettyP2PHandler handler = new(session, LimboLogs.Instance);
         handler.EnableSnappy();
 
-        // Create compressed data that will exceed MaxSnappyLength when decompressed
-        byte[] data = Snappy.CompressToArray(Enumerable.Repeat<byte>(0, SnappyParameters.MaxSnappyLength + 1).ToArray());
-
-        // Create a packet with our compressed data
-        IByteBuffer content = Unpooled.Buffer(data.Length);
-        content.WriteBytes(data);
+        IByteBuffer content = Unpooled.WrappedBuffer(data);
         ZeroPacket packet = new(content);
 
-        // Act
-        handler.ChannelRead(channelHandlerContext, packet); // releases buffer
+        handler.ChannelRead(channelHandlerContext, packet);
 
-        // Assert
         session.Received().InitiateDisconnect(DisconnectReason.BreachOfProtocol, "Max message size exceeded");
+        session.DidNotReceive().ReceiveMessage(Arg.Any<ZeroPacket>());
+        allocator.DidNotReceive().Buffer(Arg.Any<int>());
+        Assert.That(packet.ReferenceCount, Is.Zero, "the inbound packet must be released after disconnecting");
+    }
+
+    private static IEnumerable<TestCaseData> SnappyPayloadsExceedingMaxLength()
+    {
+        yield return new TestCaseData(Snappy.CompressToArray(Enumerable.Repeat<byte>(0, SnappyParameters.MaxSnappyLength + 1).ToArray()))
+            .SetName("Declared_length_exceeds_limit");
+        yield return new TestCaseData(new byte[] { 0xff, 0xff, 0xff, 0xff, 0x0f })
+            .SetName("Declared_length_overflows_int");
     }
 
     private class TestInternalNethermindException : Exception, IInternalNethermindException
```

### src/Nethermind/Nethermind.Network/P2P/ProtocolHandlers/ZeroNettyP2PHandler.cs
```diff
@@ -1,13 +1,15 @@
-// SPDX-FileCopyrightText: 2022 Demerzel Solutions Limited
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using System;
 using System.IO;
 using System.Net.Sockets;
 using DotNetty.Buffers;
+using DotNetty.Codecs;
 using DotNetty.Common.Utilities;
 using DotNetty.Transport.Channels;
 using Nethermind.Core.Exceptions;
+using Nethermind.Core.Extensions;
 using Nethermind.Logging;
 using Nethermind.Network.Rlpx;
 using Nethermind.Stats.Model;
@@ -41,15 +43,30 @@ protected override void ChannelRead0(IChannelHandlerContext ctx, ZeroPacket inpu
         }
         if (SnappyEnabled)
         {
-            int uncompressedLength = Snappy.GetUncompressedLength(
-                content.Array.AsSpan(content.ArrayOffset + content.ReaderIndex, readableBytes));
+            ReadOnlySpan<byte> snappyInput = content.Array.AsSpan(content.ArrayOffset + content.ReaderIndex, readableBytes);
+            int uncompressedLength;
+            try
+            {
+                uncompressedLength = Snappy.GetUncompressedLength(snappyInput);
+            }
+            catch (InvalidDataException exception)
+            {
+                LogSnappyDecompressionFailure(_logger, content, readableBytes);
+                throw new CorruptedFrameException(exception);
+            }
 
-            if (uncompressedLength > SnappyParameters.MaxSnappyLength)
+            if ((uint)uncompressedLength > (uint)SnappyParameters.MaxSnappyLength)
             {
                 _session.InitiateDisconnect(DisconnectReason.BreachOfProtocol, "Max message size exceeded");
                 return;
             }
 
+            if (!SnappyBlockValidator.IsValid(snappyInput, uncompressedLength))
+            {
+                LogSnappyDecompressionFailure(_logger, content, readableBytes);
+                throw new CorruptedFrameException("Invalid Snappy block");
+            }
+
             if (readableBytes > SnappyParameters.MaxSnappyLength / 4)
             {
                 if (_logger.IsTrace) _logger.Trace($"Big Snappy message of length {readableBytes}");
@@ -64,20 +81,18 @@ protected override void ChannelRead0(IChannelHandlerContext ctx, ZeroPacket inpu
             try
             {
                 int length = Snappy.Decompress(
-                    content.Array.AsSpan(content.ArrayOffset + content.ReaderIndex, readableBytes),
-                    output.Array.AsSpan(output.ArrayOffset + output.WriterIndex));
+                    snappyInput,
+                    output.Array.AsSpan(output.ArrayOffset + output.WriterIndex, uncompressedLength));
                 output.SetWriterIndex(output.WriterIndex + length);
             }
-            catch (InvalidDataException)
+            catch (InvalidDataException exception)
             {
                 output.SafeRelease();
-                // Data is not compressed sometimes, so we pass directly.
-                _session.ReceiveMessage(input);
-                return;
+                LogSnappyDecompressionFailure(_logger, content, readableBytes);
+                throw new CorruptedFrameException(exception);
             }
             catch (Exception)
             {
-                content.SkipBytes(readableBytes);
                 output.SafeRelease();
                 throw;
             }
@@ -119,8 +134,7 @@ public override void ExceptionCaught(IChannelHandlerContext context, Exception e
         else if (_session?.Node?.IsStatic != true && _session?.Node?.IsTrusted != true)
         {
             DisconnectReason reason =
-                exception is SocketException socketException &&
-                socketException.SocketErrorCode == SocketError.ConnectionReset
+                exception is SocketException { SocketErrorCode: SocketError.ConnectionReset }
                     ? DisconnectReason.ConnectionReset
                     : DisconnectReason.Exception;
             _session.InitiateDisconnect(reason, $"Error in communication with {GetClientId(_session)} ({exception.GetType().Name}): {exception.Message}");
@@ -134,5 +148,14 @@ exception is SocketException socketException &&
     private static string GetClientId(ISession? session) =>
         session?.Node?.ToString(Node.Format.Console) ?? $"unknown {session?.RemoteHost}";
 
+    private static void LogSnappyDecompressionFailure(ILogger logger, IByteBuffer content, int readableBytes)
+    {
+        if (logger.IsDebug)
+        {
+            ReadOnlyMemory<byte> prefix = content.Array.AsMemory(content.ArrayOffset + content.ReaderIndex, Math.Min(32, readableBytes));
+            logger.Debug($"Snappy decompression failed for {readableBytes} bytes: {prefix.ToHexString()}");
+        }
+    }
+
     public void EnableSnappy() => SnappyEnabled = true;
 }
```

### src/Nethermind/Nethermind.Network/P2P/Session.cs
```diff
@@ -144,8 +144,6 @@ public void EnableSnappy()
 
             // since groups were used, we are on a different thread
             _context.Channel.Pipeline.Get<ZeroNettyP2PHandler>()?.EnableSnappy();
-            // code in the next line does no longer work as if there is a packet waiting then it will skip the snappy decoder
-            // _context.Channel.Pipeline.AddBefore($"{nameof(PacketSender)}#0", null, new SnappyDecoder(_logger));
             _context.Channel.Pipeline.AddBefore($"{nameof(PacketSender)}#0", null, new ZeroSnappyEncoder(_logManager));
 
             [MethodImpl(MethodImplOptions.NoInlining)]
```

### src/Nethermind/Nethermind.Network/Rlpx/FrameHeaderReader.cs
```diff
@@ -1,4 +1,4 @@
-// SPDX-FileCopyrightText: 2025 Demerzel Solutions Limited
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using DotNetty.Buffers;
@@ -12,7 +12,8 @@ namespace Nethermind.Network.Rlpx
 {
     internal class FrameHeaderReader
     {
-        private int? _currentContextId;
+        private const int HeaderBodyOffset = 3;
+        private const int HeaderBodyLength = Frame.HeaderSize - HeaderBodyOffset;
 
         public byte[] HeaderBytes { get; } = new byte[Frame.HeaderSize];
 
@@ -23,21 +24,41 @@ public FrameInfo ReadFrameHeader(IByteBuffer input)
             frameSize = (frameSize << 8) + (HeaderBytes[1] & 0xFF);
             frameSize = (frameSize << 8) + (HeaderBytes[2] & 0xFF);
 
-            RlpReader headerBodyItems = new(HeaderBytes.AsSpan(3, 13));
-            int headerDataEnd = headerBodyItems.ReadSequenceLength() + headerBodyItems.Position;
-            int numberOfItems = headerBodyItems.PeekNumberOfItemsRemaining(headerDataEnd);
-            headerBodyItems.DecodeInt(); // not needed - adaptive IDs - DO NOT COMMENT OUT!!! - decode takes int of the RLP sequence and moves the position
-            int? contextId = numberOfItems > 1 ? headerBodyItems.DecodeInt() : (int?)null;
-            _currentContextId = contextId;
-            int? totalPacketSize = numberOfItems > 2 ? headerBodyItems.DecodeInt() : (int?)null;
+            ReadHeaderBody(out int? contextId, out int? totalPacketSize);
 
             ValidateTotalPacketSize(frameSize, totalPacketSize);
+            return new FrameInfo(frameSize, contextId, totalPacketSize);
+        }
 
-            bool isChunked = totalPacketSize.HasValue || contextId.HasValue && _currentContextId == contextId && contextId != 0;
-            bool isFirst = totalPacketSize.HasValue || !isChunked;
+        /// <summary>Decodes the RLP header body of the frame header just read into <see cref="HeaderBytes"/>.</summary>
+        /// <remarks>
+        /// Kept separate from <see cref="ReadFrameHeader"/> so that the exception handling region covers the RLP
+        /// decoding only, rather than also spanning the frame size read and <see cref="ValidateTotalPacketSize"/>.
+        /// </remarks>
+        /// <exception cref="CorruptedFrameException">The header body is not a well formed RLP sequence.</exception>
+        private void ReadHeaderBody(out int? contextId, out int? totalPacketSize)
+        {
+            try
+            {
+                RlpReader headerBodyItems = new(HeaderBytes.AsSpan(HeaderBodyOffset, HeaderBodyLength));
+                int headerDataLength = headerBodyItems.ReadSequenceLength();
+                int remaining = headerBodyItems.Length - headerBodyItems.Position;
+                if ((uint)headerDataLength > (uint)remaining)
+                {
+                    throw new CorruptedFrameException($"Invalid Rlpx header lengths, header body RLP length {headerDataLength} exceeds the {remaining} bytes left in the header");
+                }
 
-            headerBodyItems.Check(headerDataEnd);
-            return new FrameInfo(isChunked, isFirst, frameSize, totalPacketSize ?? frameSize);
+                int headerDataEnd = headerDataLength + headerBodyItems.Position;
+                int numberOfItems = headerBodyItems.PeekNumberOfItemsRemaining(headerDataEnd);
+                headerBodyItems.DecodeInt(); // not needed - adaptive IDs - DO NOT COMMENT OUT!!! - decode takes int of the RLP sequence and moves the position
+                contextId = numberOfItems > 1 ? headerBodyItems.DecodeInt() : (int?)null;
+                totalPacketSize = numberOfItems > 2 ? headerBodyItems.DecodeInt() : (int?)null;
+                headerBodyItems.Check(headerDataEnd);
+            }
+            catch (Exception exception) when (exception is RlpException or ArgumentOutOfRangeException or IndexOutOfRangeException)
+            {
+                throw new CorruptedFrameException(exception);
+            }
         }
 
         private static void ValidateTotalPacketSize(int frameSize, int? totalPacketSize)
@@ -59,12 +80,11 @@ private static void ValidateTotalPacketSize(int frameSize, int? totalPacketSize)
             static void ThrowCorruptedFrameException(int frameSize, int totalPacketSize) => throw new CorruptedFrameException($"Invalid Rlpx header lengths, packet size {totalPacketSize}, frame size {frameSize}");
         }
 
-        internal readonly struct FrameInfo(bool isChunked, bool isFirst, int size, int totalPacketSize)
+        internal readonly struct FrameInfo(int size, int? contextId, int? totalPacketSize)
         {
-            public bool IsChunked { get; } = isChunked;
-            public bool IsFirst { get; } = isFirst;
             public int Size { get; } = size;
-            public int TotalPacketSize { get; } = totalPacketSize;
+            public int? ContextId { get; } = contextId;
+            public int? TotalPacketSize { get; } = totalPacketSize;
             public int Padding => Frame.CalculatePadding(Size);
 
             public int PayloadSize => Size + Padding;
```

### src/Nethermind/Nethermind.Network/Rlpx/SnappyBlockValidator.cs
```diff
@@ -0,0 +1,168 @@
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
+// SPDX-License-Identifier: LGPL-3.0-only
+
+using System;
+using System.Buffers.Binary;
+
+namespace Nethermind.Network.Rlpx;
+
+internal static class SnappyBlockValidator
+{
+    /// <summary>Checks that a raw Snappy block consumes all input and produces exactly its declared length.</summary>
+    /// <remarks>
+    /// Snappier accepts trailing commands after reaching the declared length, so peer input needs a strict structural
+    /// pass before decompression.
+    /// </remarks>
+    public static bool IsValid(ReadOnlySpan<byte> input, int expectedLength)
+    {
+        if ((uint)expectedLength > SnappyParameters.MaxSnappyLength ||
+            !TryReadUncompressedLength(input, out int position, out uint declaredLength) ||
+            declaredLength != (uint)expectedLength)
+        {
+            return false;
+        }
+
+        int written = 0;
+        while (position < input.Length)
+        {
+            byte tag = input[position++];
+            switch (tag & 0x03)
+            {
+                case 0:
+                    if (!TryReadLiteral(input, tag, expectedLength - written, ref position, out int literalLength))
+                    {
+                        return false;
+                    }
+
+                    written += literalLength;
+                    break;
+                case 1:
+                    if (position >= input.Length ||
+                        !TryApplyCopy(
+                            4 + ((tag >> 2) & 0x07),
+                            (uint)((tag & 0xe0) << 3) | input[position++],
+                            expectedLength,
+                            ref written))
+                    {
+                        return false;
+                    }
+
+                    break;
+                case 2:
+                    if (input.Length - position < sizeof(ushort) ||
+                        !TryApplyCopy(
+                            1 + (tag >> 2),
+                            BinaryPrimitives.ReadUInt16LittleEndian(input[position..]),
+                            expectedLength,
+                            ref written))
+                    {
+                        return false;
+                    }
+
+                    position += sizeof(ushort);
+                    break;
+                default:
+                    if (input.Length - position < sizeof(uint) ||
+                        !TryApplyCopy(
+                            1 + (tag >> 2),
+                            BinaryPrimitives.ReadUInt32LittleEndian(input[position..]),
+                            expectedLength,
+                            ref written))
+                    {
+                        return false;
+                    }
+
+                    position += sizeof(uint);
+                    break;
+            }
+        }
+
+        return written == expectedLength;
+    }
+
+    private static bool TryReadUncompressedLength(ReadOnlySpan<byte> input, out int position, out uint length)
+    {
+        length = 0;
+        position = 0;
+        for (int shift = 0; shift <= 28; shift += 7)
+        {
+            if (position >= input.Length)
+            {
+                return false;
+            }
+
+            byte current = input[position++];
+            if (shift == 28 && (current & 0xf0) != 0)
+            {
+                return false;
+            }
+
+            length |= (uint)(current & 0x7f) << shift;
+            if ((current & 0x80) == 0)
+            {
+                return true;
+            }
+        }
+
+        return false;
+    }
+
+    private static bool TryReadLiteral(
+        ReadOnlySpan<byte> input,
+        byte tag,
+        int remainingOutput,
+        ref int position,
+        out int literalLength)
+    {
+        int lengthCode = tag >> 2;
+        if (lengthCode < 60)
+        {
+            literalLength = lengthCode + 1;
+        }
+        else
+        {
+            int lengthBytes = lengthCode - 59;
+            if (input.Length - position < lengthBytes)
+            {
+                literalLength = 0;
+                return false;
+            }
+
+            uint lengthMinusOne = lengthBytes switch
+            {
+                1 => input[position],
+                2 => BinaryPrimitives.ReadUInt16LittleEndian(input[position..]),
+                3 => (uint)(input[position] | input[position + 1] << 8 | input[position + 2] << 16),
+                _ => BinaryPrimitives.ReadUInt32LittleEndian(input[position..])
+            };
+            position += lengthBytes;
+
+            if (lengthMinusOne >= (uint)remainingOutput)
+            {
+                literalLength = 0;
+                return false;
+            }
+
+            literalLength = (int)lengthMinusOne + 1;
+        }
+
+        if (literalLength > remainingOutput || input.Length - position < literalLength)
+        {
+            return false;
+        }
+
+        position += literalLength;
+        return true;
+    }
+
+    private static bool TryApplyCopy(int length, uint offset, int expectedLength, ref int written)
+    {
+        if (offset == 0 || offset > (uint)written || length > expectedLength - written)
+        {
+            return false;
+        }
+
+        written += length;
+        return true;
+    }
+}
```

### src/Nethermind/Nethermind.Network/Rlpx/SnappyDecoder.cs
```diff
@@ -1,44 +0,0 @@
-// SPDX-FileCopyrightText: 2022 Demerzel Solutions Limited
-// SPDX-License-Identifier: LGPL-3.0-only
-
-using System;
-using System.Collections.Generic;
-using DotNetty.Codecs;
-using DotNetty.Transport.Channels;
-using Nethermind.Core.Extensions;
-using Nethermind.Logging;
-using Snappier;
-
-namespace Nethermind.Network.Rlpx;
-
-public class SnappyDecoder(ILogger logger) : MessageToMessageDecoder<Packet>
-{
-    protected override void Decode(IChannelHandlerContext context, Packet message, List<object> output)
-    {
-        if (Snappy.GetUncompressedLength(message.Data) > SnappyParameters.MaxSnappyLength)
-        {
-            throw new Exception("Max message size exceeded");
-        }
-
-        if (message.Data.Length > SnappyParameters.MaxSnappyLength / 4)
-        {
-            if (logger.IsWarn) logger.Warn($"Big Snappy message of length {message.Data.Length}");
-        }
-        else
-        {
-            if (logger.IsTrace) logger.Trace($"Decompressing with Snappy a message of length {message.Data.Length}");
-        }
-
-        try
-        {
-            message.Data = Snappy.DecompressToArray(message.Data);
-        }
-        catch
-        {
-            logger.Error($"{message.Data.ToHexString()}");
-            throw;
-        }
-
-        output.Add(message);
-    }
-}
```

### src/Nethermind/Nethermind.Network/Rlpx/ZeroFrameMerger.cs
```diff
@@ -1,8 +1,10 @@
-// SPDX-FileCopyrightText: 2022 Demerzel Solutions Limited
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using System;
 using System.Collections.Generic;
+using System.Diagnostics;
+using System.Diagnostics.CodeAnalysis;
 using System.Runtime.CompilerServices;
 using DotNetty.Buffers;
 using DotNetty.Codecs;
@@ -18,12 +20,13 @@ public class ZeroFrameMerger(ILogManager logManager) : ByteToMessageDecoder
         private readonly ILogger _logger = logManager?.GetClassLogger<ZeroFrameMerger>() ?? throw new ArgumentNullException(nameof(logManager));
 
         private ZeroPacket? _zeroPacket;
+        private int? _currentContextId;
         private readonly FrameHeaderReader _headerReader = new();
 
         public override void HandlerRemoved(IChannelHandlerContext context)
         {
             base.HandlerRemoved(context);
-            _zeroPacket?.Release();
+            ReleaseInProgressPacket();
         }
 
         protected override void Decode(IChannelHandlerContext context, IByteBuffer input, List<object> output)
@@ -41,57 +44,99 @@ protected override void Decode(IChannelHandlerContext context, IByteBuffer input
                 throw new IllegalReferenceCountException(input.ReferenceCount);
             }
 
+            try
+            {
+                DecodeFrame(context, input, output);
+            }
+            catch
+            {
+                ReleaseInProgressPacket();
+                // The upstream decoder emits exactly one complete frame per input. Do not retain the rejected
+                // frame's payload and padding in ByteToMessageDecoder's cumulation when the peer stays connected.
+                input.SkipBytes(input.ReadableBytes);
+                throw;
+            }
+        }
+
+        private void DecodeFrame(IChannelHandlerContext context, IByteBuffer input, List<object> output)
+        {
             FrameHeaderReader.FrameInfo frame = _headerReader.ReadFrameHeader(input);
-            if (frame.IsFirst)
+            if (frame.TotalPacketSize.HasValue || _zeroPacket is null)
             {
                 if (_zeroPacket is not null)
                 {
-                    // Offending frame is intentionally not processed: the CorruptedFrameException
-                    // propagates up the pipeline and closes the peer connection.
-                    _zeroPacket.Release();
-                    _zeroPacket = null;
+                    // Offending frame is intentionally not processed; the CorruptedFrameException propagates
+                    // through the pipeline for the peer handler to classify.
+                    ReleaseInProgressPacket();
                     throw new CorruptedFrameException($"{nameof(ZeroFrameMerger)} received a new first chunk before the in-progress packet completed");
                 }
 
                 ReadFirstChunk(context, input, frame);
+                _currentContextId = frame.TotalPacketSize.HasValue ? frame.ContextId : null;
             }
             else
             {
-                if (_zeroPacket is null)
+                if (frame.ContextId != _currentContextId)
                 {
-                    throw new CorruptedFrameException($"{nameof(ZeroFrameMerger)} received a continuation chunk with no in-progress packet");
+                    int? expectedContextId = _currentContextId;
+                    ReleaseInProgressPacket();
+                    ThrowUnexpectedContextId(frame.ContextId, expectedContextId);
                 }
 
                 ReadChunk(input, frame);
             }
 
-            if (!_zeroPacket.Content.IsWritable())
-            {
-                input.SkipBytes(frame.Padding);
-                output.Add(_zeroPacket);
-                _zeroPacket = null;
+            input.SkipBytes(frame.Padding);
 
+            if (_zeroPacket.Content.MaxWritableBytes == 0)
+            {
+                ZeroPacket completedPacket = _zeroPacket!;
                 if (input.IsReadable())
                 {
                     throw new CorruptedFrameException($"{nameof(ZeroFrameMerger)} received a corrupted frame - {input.ReadableBytes} longer than expected");
                 }
+
+                output.Add(completedPacket);
+                ResetInProgressPacket();
             }
         }
 
         [MethodImpl(MethodImplOptions.AggressiveInlining)]
-        private void ReadChunk(IByteBuffer input, in FrameHeaderReader.FrameInfo frame) => input.ReadBytes(_zeroPacket.Content, frame.Size);
+        private void ReadChunk(IByteBuffer input, in FrameHeaderReader.FrameInfo frame)
+        {
+            if (frame.Size > _zeroPacket.Content.MaxWritableBytes)
+            {
+                int remainingPacketSize = _zeroPacket.Content.MaxWritableBytes;
+                ReleaseInProgressPacket();
+                ThrowFrameSizeExceedsRemaining(frame.Size, remainingPacketSize);
+            }
+
+            _zeroPacket.Content.EnsureWritable(frame.Size);
+            input.ReadBytes(_zeroPacket.Content, frame.Size);
+        }
 
         [MethodImpl(MethodImplOptions.AggressiveInlining)]
         private void ReadFirstChunk(IChannelHandlerContext context, IByteBuffer input, in FrameHeaderReader.FrameInfo frame)
         {
-            RlpReader reader = new(input.AsSpan());
-            ulong rlpPacketType = reader.DecodeULong();
-            int read = reader.Position;
+            ulong rlpPacketType = DecodePacketType(input, out int read);
+
+            if (read > frame.Size)
+            {
+                ThrowPacketTypeLengthExceedsFrameSize(read, frame.Size);
+            }
+
+            if (rlpPacketType > byte.MaxValue)
+            {
+                ThrowPacketTypeOutOfRange(rlpPacketType);
+            }
+
             input.SkipBytes(read);
             IByteBuffer content;
-            if (frame.IsChunked)
+            if (frame.TotalPacketSize.HasValue)
             {
-                content = context.Allocator.Buffer(frame.TotalPacketSize - read);
+                int initialContentSize = frame.Size - read;
+                int totalContentSize = frame.TotalPacketSize.Value - read;
+                content = context.Allocator.Buffer(initialContentSize, totalContentSize);
             }
             else
             {
@@ -103,13 +148,61 @@ private void ReadFirstChunk(IChannelHandlerContext context, IByteBuffer input, i
                 PacketType = (byte)rlpPacketType
             };
 
-            // If not chunked, then we already used a slice of the input,
-            // otherwise we need to read into the freshly allocated buffer.
-            if (frame.IsChunked)
+            if (frame.TotalPacketSize.HasValue)
             {
                 input.ReadBytes(_zeroPacket.Content, frame.Size - read);
-                // do not call Release since the input buffer is managed by
             }
         }
+
+        private void ReleaseInProgressPacket()
+        {
+            _zeroPacket?.Release();
+            ResetInProgressPacket();
+        }
+
+        private void ResetInProgressPacket()
+        {
+            _zeroPacket = null;
+            _currentContextId = null;
+        }
+
+        /// <remarks>
+        /// The try/catch lives here rather than in <see cref="ReadFirstChunk"/> so that the caller stays free of an
+        /// exception handling region, which RyuJIT refuses to inline.
+        /// </remarks>
+        private static ulong DecodePacketType(IByteBuffer input, out int read)
+        {
+            try
+            {
+                RlpReader reader = new(input.AsSpan());
+                ulong packetType = reader.DecodeULong();
+                read = reader.Position;
+                return packetType;
+            }
+            catch (Exception exception) when (exception is RlpException or ArgumentOutOfRangeException or IndexOutOfRangeException)
+            {
+                throw new CorruptedFrameException(exception);
+            }
+        }
+
+        [DoesNotReturn, StackTraceHidden]
+        private static void ThrowFrameSizeExceedsRemaining(int frameSize, int remainingPacketSize)
+            => throw new CorruptedFrameException(
+                $"{nameof(ZeroFrameMerger)} frame size {frameSize} exceeds remaining packet size {remainingPacketSize}");
+
+        [DoesNotReturn, StackTraceHidden]
+        private static void ThrowPacketTypeLengthExceedsFrameSize(int packetTypeLength, int frameSize)
+            => throw new CorruptedFrameException(
+                $"{nameof(ZeroFrameMerger)} packet type length {packetTypeLength} exceeds frame size {frameSize}");
+
+        [DoesNotReturn, StackTraceHidden]
+        private static void ThrowPacketTypeOutOfRange(ulong packetType)
+            => throw new CorruptedFrameException(
+                $"{nameof(ZeroFrameMerger)} packet type {packetType} does not fit in a byte");
+
+        [DoesNotReturn, StackTraceHidden]
+        private static void ThrowUnexpectedContextId(int? contextId, int? expectedContextId)
+            => throw new CorruptedFrameException(
+                $"{nameof(ZeroFrameMerger)} continuation frame context id {contextId} does not match in-progress packet context id {expectedContextId}");
     }
 }
```
