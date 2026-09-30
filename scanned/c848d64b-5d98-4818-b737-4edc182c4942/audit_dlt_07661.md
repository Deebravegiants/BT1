# [?] Fix overflow exception on decoding due to negative long field (#4167)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2022-06-20
Source: https://github.com/NethermindEth/nethermind/commit/5614f91e3d2f0bdad8c15602179d4161933fb88a
Type: security-commit

## Details
Fix overflow exception on decoding due to negative long field (#4167)

* Fix overflow exception on decoding due to negative long field

* Added fix when decoding via span

## Patch
### src/Nethermind/Nethermind.Core.Test/Encoding/HeaderDecoderTests.cs
```diff
@@ -119,5 +119,39 @@ public void Can_encode_decode_with_base_fee()
                 HeaderDecoder.Eip1559TransitionBlock = long.MaxValue;
             }
         }
+        
+        [TestCase(-1)]
+        [TestCase(long.MinValue)]
+        public void Can_encode_decode_with_negative_long_fields(long negativeLong)
+        {
+            BlockHeader header = Build.A.BlockHeader.
+                WithNumber(negativeLong).
+                WithGasUsed(negativeLong).
+                WithGasLimit(negativeLong).TestObject;
+            
+            Rlp rlp = Rlp.Encode(header);
+            BlockHeader blockHeader = Rlp.Decode<BlockHeader>(rlp);
+            
+            blockHeader.GasUsed.Should().Be(negativeLong);
+            blockHeader.Number.Should().Be(negativeLong);
+            blockHeader.GasLimit.Should().Be(negativeLong);
+        }
+        
+        [TestCase(-1)]
+        [TestCase(long.MinValue)]
+        public void Can_encode_decode_with_negative_long_when_using_span(long negativeLong)
+        {
+            BlockHeader header = Build.A.BlockHeader.
+                WithNumber(negativeLong).
+                WithGasUsed(negativeLong).
+                WithGasLimit(negativeLong).TestObject;
+            
+            Rlp rlp = Rlp.Encode(header);
+            BlockHeader blockHeader = Rlp.Decode<BlockHeader>(rlp.Bytes.AsSpan());
+            
+            blockHeader.GasUsed.Should().Be(negativeLong);
+            blockHeader.Number.Should().Be(negativeLong);
+            blockHeader.GasLimit.Should().Be(negativeLong);
+        }
     }
 }
```

### src/Nethermind/Nethermind.Serialization.Rlp/HeaderDecoder.cs
```diff
@@ -48,9 +48,9 @@ public class HeaderDecoder : IRlpValueDecoder<BlockHeader>, IRlpStreamDecoder<Bl
             Keccak? receiptsRoot = decoderContext.DecodeKeccak();
             Bloom? bloom = decoderContext.DecodeBloom();
             UInt256 difficulty = decoderContext.DecodeUInt256();
-            UInt256 number = decoderContext.DecodeUInt256();
-            UInt256 gasLimit = decoderContext.DecodeUInt256();
-            UInt256 gasUsed = decoderContext.DecodeUInt256();
+            long number = decoderContext.DecodeLong();
+            long gasLimit = decoderContext.DecodeLong();
+            long gasUsed = decoderContext.DecodeLong();
             UInt256 timestamp = decoderContext.DecodeUInt256();
             byte[]? extraData = decoderContext.DecodeByteArray();
 
@@ -59,16 +59,16 @@ public class HeaderDecoder : IRlpValueDecoder<BlockHeader>, IRlpStreamDecoder<Bl
                 unclesHash,
                 beneficiary,
                 difficulty,
-                (long)number,
-                (long)gasLimit,
+                number,
+                gasLimit,
                 timestamp,
                 extraData)
             {
                 StateRoot = stateRoot,
                 TxRoot = transactionsRoot,
                 ReceiptsRoot = receiptsRoot,
                 Bloom = bloom,
-                GasUsed = (long)gasUsed,
+                GasUsed = gasUsed,
                 Hash = Keccak.Compute(headerRlp)
             };
 
@@ -116,9 +116,9 @@ public class HeaderDecoder : IRlpValueDecoder<BlockHeader>, IRlpStreamDecoder<Bl
             Keccak? receiptsRoot = rlpStream.DecodeKeccak();
             Bloom? bloom = rlpStream.DecodeBloom();
             UInt256 difficulty = rlpStream.DecodeUInt256();
-            UInt256 number = rlpStream.DecodeUInt256();
-            UInt256 gasLimit = rlpStream.DecodeUInt256();
-            UInt256 gasUsed = rlpStream.DecodeUInt256();
+            long number = rlpStream.DecodeLong();
+            long gasLimit = rlpStream.DecodeLong();
+            long gasUsed = rlpStream.DecodeLong();
             UInt256 timestamp = rlpStream.DecodeUInt256();
             byte[]? extraData = rlpStream.DecodeByteArray();
 
@@ -127,16 +127,16 @@ public class HeaderDecoder : IRlpValueDecoder<BlockHeader>, IRlpStreamDecoder<Bl
                 unclesHash,
                 beneficiary,
                 difficulty,
-                (long)number,
-                (long)gasLimit,
+                number,
+                gasLimit,
                 timestamp,
                 extraData)
             {
                 StateRoot = stateRoot,
                 TxRoot = transactionsRoot,
                 ReceiptsRoot = receiptsRoot,
                 Bloom = bloom,
-                GasUsed = (long)gasUsed,
+                GasUsed = gasUsed,
                 Hash = Keccak.Compute(headerRlp)
             };
 
```
