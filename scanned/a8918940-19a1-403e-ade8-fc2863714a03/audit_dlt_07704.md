# [?] Fixes: GHSA-h594-ww62-rcxv fix logging issue with invalid discv4 packet (#11093)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2026-08-20
Source: https://github.com/besu-eth/besu/commit/de54bf9be0aa37c057a5f9b9e924aa3f09c504b1
Type: security-commit

## Details
Fixes: GHSA-h594-ww62-rcxv fix logging issue with invalid discv4 packet (#11093)

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -67,6 +67,7 @@
 - Removed the legacy `PANTHEON_` environment variable prefix for configuration options, everyone should already use the `BESU_` prefix at this time.
 
 ### Bug fixes
+- Improve logging for malformed discv4 UDP packets.
 - Remove `System.out`/`System.err` logging from `P256VerifyPrecompiledContract` and `BlockchainQueries` — these could leak sensitive data to stdout/stderr in production.
 - EIP-1459 DNS discovery now rejoins TXT records split across multiple `<character-string>`s. Records longer than 255 bytes were truncated, so Besu silently discarded most of every tree, resolving 832 of 3000 nodes from the mainnet tree. [#10985](https://github.com/besu-eth/besu/pull/10985)
 - Queue backward-sync targets received before peer readiness and retry when a peer connects. [#10843](https://github.com/besu-eth/besu/pull/10843)
```

### ethereum/p2p/src/main/java/org/hyperledger/besu/ethereum/p2p/discovery/discv4/internal/packet/PacketDeserializer.java
```diff
@@ -85,15 +85,15 @@ public Packet decode(final Bytes message) {
           case ENR_REQUEST -> enrRequestPacketDataRlpReader;
           case ENR_RESPONSE -> enrResponsePacketDataRlpReader;
         };
-    final PacketData packetData;
     try {
-      packetData = deserializer.readFrom(RLP.input(message.slice(Packet.PACKET_DATA_INDEX)));
+      final PacketData packetData =
+          deserializer.readFrom(RLP.input(message.slice(Packet.PACKET_DATA_INDEX)));
+      return packetFactory.create(packetType, packetData, message);
     } catch (final RLPException e) {
       throw new PeerDiscoveryPacketDecodingException("Malformed packet of type: " + packetType, e);
     } catch (final IllegalArgumentException e) {
       throw new PeerDiscoveryPacketDecodingException(
           "Failed decoding packet of type: " + packetType, e);
     }
-    return packetFactory.create(packetType, packetData, message);
   }
 }
```

### ethereum/p2p/src/test/java/org/hyperledger/besu/ethereum/p2p/discovery/discv4/internal/packet/PacketDeserializerTest.java
```diff
@@ -14,8 +14,10 @@
  */
 package org.hyperledger.besu.ethereum.p2p.discovery.discv4.internal.packet;
 
+import org.hyperledger.besu.crypto.Hash;
 import org.hyperledger.besu.crypto.SECPSignature;
 import org.hyperledger.besu.crypto.SignatureAlgorithmFactory;
+import org.hyperledger.besu.ethereum.p2p.discovery.PeerDiscoveryPacketDecodingException;
 import org.hyperledger.besu.ethereum.p2p.discovery.discv4.Endpoint;
 import org.hyperledger.besu.ethereum.p2p.discovery.discv4.internal.PacketType;
 import org.hyperledger.besu.ethereum.p2p.discovery.discv4.internal.packet.enrrequest.EnrRequestPacketData;
@@ -225,6 +227,52 @@ public void testDecodeForEnrRequestPacket() {
     Assertions.assertEquals(456, actualPacketData.getExpiration());
   }
 
+  @Test
+  public void testDecodeWithOutOfBoundsSignatureThrowsDecodingException() {
+    // Crafted invalid packet with r=0 in the signature (out of the valid SECP256k1 range [1, n)).
+    final Bytes sig =
+        Bytes.concatenate(
+            Bytes.repeat((byte) 0x00, 32), Bytes.repeat((byte) 0x01, 32), Bytes.of(0x00));
+    final Bytes type = Bytes.of(0x05); // ENR_REQUEST
+    final Bytes body = Bytes.of(0xc5, 0x84, 0xff, 0xff, 0xff, 0xff); // RLP [0xFFFFFFFF] expiration
+    final Bytes rest = Bytes.concatenate(sig, type, body);
+    final Bytes packet = Bytes.concatenate(Hash.keccak256(rest), rest);
+
+    Assertions.assertThrows(
+        PeerDiscoveryPacketDecodingException.class, () -> packetDeserializer.decode(packet));
+  }
+
+  @Test
+  public void testDecodeWithInvalidRecIdThrowsDecodingException() {
+    // recId = 0x02 is outside {0, 1} — SECPSignature.create() throws IllegalArgumentException.
+    final Bytes sig =
+        Bytes.concatenate(
+            Bytes.repeat((byte) 0x01, 32), Bytes.repeat((byte) 0x01, 32), Bytes.of(0x02));
+    final Bytes type = Bytes.of(0x05); // ENR_REQUEST
+    final Bytes body = Bytes.of(0xc5, 0x84, 0xff, 0xff, 0xff, 0xff);
+    final Bytes rest = Bytes.concatenate(sig, type, body);
+    final Bytes packet = Bytes.concatenate(Hash.keccak256(rest), rest);
+
+    Assertions.assertThrows(
+        PeerDiscoveryPacketDecodingException.class, () -> packetDeserializer.decode(packet));
+  }
+
+  @Test
+  public void testDecodeWithOutOfBoundsSThrowsDecodingException() {
+    // s=0 is outside the valid SECP256k1 range [1, n) — exercises the same checkInBounds path as
+    // r=0 but via the s field.
+    final Bytes sig =
+        Bytes.concatenate(
+            Bytes.repeat((byte) 0x01, 32), Bytes.repeat((byte) 0x00, 32), Bytes.of(0x00));
+    final Bytes type = Bytes.of(0x05); // ENR_REQUEST
+    final Bytes body = Bytes.of(0xc5, 0x84, 0xff, 0xff, 0xff, 0xff);
+    final Bytes rest = Bytes.concatenate(sig, type, body);
+    final Bytes packet = Bytes.concatenate(Hash.keccak256(rest), rest);
+
+    Assertions.assertThrows(
+        PeerDiscoveryPacketDecodingException.class, () -> packetDeserializer.decode(packet));
+  }
+
   @Test
   public void testDecodeForEnrResponsePacket() {
     String packetHex =
```
