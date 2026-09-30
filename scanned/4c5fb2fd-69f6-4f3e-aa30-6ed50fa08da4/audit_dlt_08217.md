# [?] Remove PacketDeserializer's extra overflow guard (#29715)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-01-17
Source: https://github.com/solana-labs/solana/commit/156454c9808457d8fb8c8cd7ade5e4346f56bf84
Type: security-commit

## Details
Remove PacketDeserializer's extra overflow guard (#29715)

## Patch
### core/src/packet_deserializer.rs
```diff
@@ -84,17 +84,23 @@ impl PacketDeserializer {
         packet_count_upperbound: usize,
     ) -> Result<(Vec<PacketBatch>, Option<SigverifyTracerPacketStats>), RecvTimeoutError> {
         let start = Instant::now();
-        let (mut packet_batches, mut aggregated_tracer_packet_stats_option) =
+
+        let (mut packet_batches_received_so_far, mut aggregated_tracer_packet_stats_option) =
             self.packet_batch_receiver.recv_timeout(recv_timeout)?;
+        let mut num_packets_received = packet_batches_received_so_far
+            .iter()
+            .map(|batch| batch.len())
+            .sum::<usize>();
 
-        let mut num_packets_received: usize = packet_batches.iter().map(|batch| batch.len()).sum();
-        while let Ok((packet_batch, tracer_packet_stats_option)) =
+        while let Ok((packet_batches, tracer_packet_stats_option)) =
             self.packet_batch_receiver.try_recv()
         {
             trace!("got more packet batches in packet deserializer");
-            let (packets_received, packet_count_overflowed) = num_packets_received
-                .overflowing_add(packet_batch.iter().map(|batch| batch.len()).sum());
-            packet_batches.extend(packet_batch);
+            num_packets_received += packet_batches
+                .iter()
+                .map(|batch| batch.len())
+                .sum::<usize>();
+            packet_batches_received_so_far.extend(packet_batches);
 
             if let Some(tracer_packet_stats) = &tracer_packet_stats_option {
                 if let Some(aggregated_tracer_packet_stats) =
@@ -106,16 +112,15 @@ impl PacketDeserializer {
                 }
             }
 
-            if start.elapsed() >= recv_timeout
-                || packet_count_overflowed
-                || packets_received >= packet_count_upperbound
-            {
+            if start.elapsed() >= recv_timeout || num_packets_received >= packet_count_upperbound {
                 break;
             }
-            num_packets_received = packets_received;
         }
 
-        Ok((packet_batches, aggregated_tracer_packet_stats_option))
+        Ok((
+            packet_batches_received_so_far,
+            aggregated_tracer_packet_stats_option,
+        ))
     }
 
     fn generate_packet_indexes(packet_batch: &PacketBatch) -> Vec<usize> {
```
