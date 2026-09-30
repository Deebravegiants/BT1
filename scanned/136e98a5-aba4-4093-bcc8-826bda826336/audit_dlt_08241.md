# [?] watch: fix gauge underflow

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-08-05
Source: https://github.com/firedancer-io/firedancer/commit/3f11aa3b4af685d078820e1068d6237507f80658
Type: security-commit

## Details
watch: fix gauge underflow

Fixes an unsigned integer underflow bug in watch.c when gauges
reset to zero.  (e.g. the 'accounts per second' view after
aborting a snapshot load)

## Patch
### src/app/shared/commands/watch/watch.c
```diff
@@ -181,18 +181,23 @@ diff_link( config_t const * config,
   return result;
 }
 
-static long
+/* diff_tile returns the positive increase between the last and current
+   value of an increasing counter.  Clamps wraparound to zero (this
+   happens to gauge-based counters, e.g. "number of events in an epoch") */
+
+static ulong
 diff_tile( config_t const * config,
            char const *     tile_name,
            ulong const *    prev_tile,
            ulong const *    cur_tile,
            ulong            idx ) {
-  long result = 0L;
-
+  ulong result = 0UL;
   for( ulong i=0UL; i<config->topo.tile_cnt; i++ ) {
     fd_topo_tile_t const * tile = &config->topo.tiles[ i ];
     if( FD_UNLIKELY( strcmp( tile->name, tile_name ) ) ) continue;
-    result += (long)cur_tile[ i*FD_METRICS_TOTAL_SZ+idx ]-(long)prev_tile[ i*FD_METRICS_TOTAL_SZ+idx ];
+    ulong prev = prev_tile[ i*FD_METRICS_TOTAL_SZ+idx ];
+    ulong cur  =  cur_tile[ i*FD_METRICS_TOTAL_SZ+idx ];
+    result += cur>=prev ? cur-prev : 0UL;
   }
   return result;
 }
@@ -440,8 +445,8 @@ fmt_bar( char * buf,
   }))
 
 #define DIFF_BYTES( tile_name, metric_type, metric_subtype, metric ) (__extension__({ \
-    long bytes = diff_tile( config, tile_name, prev_tile, cur_tile, MIDX( metric_type, metric_subtype, metric ) ); \
-     fmt_bytes( fd_alloca_check( 1UL, 64UL ), 64UL, bytes );                               \
+    ulong bytes = diff_tile( config, tile_name, prev_tile, cur_tile, MIDX( metric_type, metric_subtype, metric ) ); \
+     fmt_bytes( fd_alloca_check( 1UL, 64UL ), 64UL, (long)bytes );                          \
   }))
 
 #define COUNT( count ) (__extension__({                     \
@@ -1262,17 +1267,17 @@ write_gui( config_t const * config,
   double gui_idle_pct  = 100.0*(double)diff_tile( config, gui_name, prev_tile, cur_tile, MIDX( COUNTER, TILE, REGIME_DURATION_NANOS_CAUGHT_UP_POSTFRAG ) )/(double)gui_total_ticks;
   double gui_busy_pct  = 100.0 - gui_backp_pct - gui_idle_pct;
 
-  long sent_frame_count = diff_tile( config, gui_name, prev_tile, cur_tile, off_websocket_frame_tx );
-  char * sent_frame_count_s = COUNT( (ulong)sent_frame_count );
-  long received_frame_count = diff_tile( config, gui_name, prev_tile, cur_tile, off_websocket_frame_rx );
+  ulong sent_frame_count = diff_tile( config, gui_name, prev_tile, cur_tile, off_websocket_frame_tx );
+  char * sent_frame_count_s = COUNT( sent_frame_count );
+  ulong received_frame_count = diff_tile( config, gui_name, prev_tile, cur_tile, off_websocket_frame_rx );
 
   PRINT( ROWH( "◉", CYAN, "gui         " )
          K( "conns" ) "%lu"
          K( "frames" ) "%s" U( " in" ) " %s" U( " out" )
          K( "bw" ) "%s" U( " in" ) " %s" U( " out" )
          K( "busy" ) "%s%3.0f" U( "%%" ) RESET CLEARLN "\n",
     connection_count,
-    COUNT( (ulong)received_frame_count ),
+    COUNT( received_frame_count ),
     sent_frame_count_s,
     bytes_read_s,
     bytes_written_s,
@@ -1645,36 +1650,36 @@ run( config_t const * config,
       snap_links( &config->topo, links+last_snap*(cons_cnt*8UL*FD_METRICS_ALL_LINK_IN_TOTAL) );
 
       /* Bench */
-      tps_sent_samples[ tps_sent_samples_idx%(sizeof(tps_sent_samples)/sizeof(tps_sent_samples[0])) ] = (ulong)diff_tile( config, "benchs", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, BENCHS, TXN_TX ) );
+      tps_sent_samples[ tps_sent_samples_idx%(sizeof(tps_sent_samples)/sizeof(tps_sent_samples[0])) ] = diff_tile( config, "benchs", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, BENCHS, TXN_TX ) );
       tps_sent_samples_idx++;
 
       /* Replay */
-      sps_samples[ sps_samples_idx%(sizeof(sps_samples)/sizeof(sps_samples[0])) ] = (ulong)diff_tile( config, "replay", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, REPLAY, SLOT_REPLAYED ) );
+      sps_samples[ sps_samples_idx%(sizeof(sps_samples)/sizeof(sps_samples[0])) ] = diff_tile( config, "replay", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, REPLAY, SLOT_REPLAYED ) );
       sps_samples_idx++;
-      tps_samples[ tps_samples_idx%(sizeof(tps_samples)/sizeof(tps_samples[0])) ] = (ulong)diff_tile( config, "replay", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, REPLAY, TXN_PROCESSED ) );
+      tps_samples[ tps_samples_idx%(sizeof(tps_samples)/sizeof(tps_samples[0])) ] = diff_tile( config, "replay", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, REPLAY, TXN_PROCESSED ) );
       tps_samples_idx++;
       cups_samples[ cups_samples_idx%(sizeof(cups_samples)/sizeof(cups_samples[0])) ] =
-          (ulong)diff_tile( config, "execrp", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, EXECRP, CU_EXECUTED ) ) +
-          (ulong)diff_tile( config, "execle", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, EXECLE, CU_EXECUTED ) );
+          diff_tile( config, "execrp", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, EXECRP, CU_EXECUTED ) ) +
+          diff_tile( config, "execle", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, EXECLE, CU_EXECUTED ) );
       cups_samples_idx++;
 
       /* Snapshot */
-      snapshot_rx_samples[ snapshot_rx_idx%(sizeof(snapshot_rx_samples)/sizeof(snapshot_rx_samples[0])) ] = (ulong)diff_tile( config, "snapct", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( GAUGE, SNAPCT, FULL_BYTES_READ ) ) +
-                                                                                                            (ulong)diff_tile( config, "snapct", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( GAUGE, SNAPCT, INCREMENTAL_BYTES_READ ) );
+      snapshot_rx_samples[ snapshot_rx_idx%(sizeof(snapshot_rx_samples)/sizeof(snapshot_rx_samples[0])) ] = diff_tile( config, "snapct", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( GAUGE, SNAPCT, FULL_BYTES_READ ) ) +
+                                                                                                            diff_tile( config, "snapct", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( GAUGE, SNAPCT, INCREMENTAL_BYTES_READ ) );
       snapshot_rx_idx++;
-      snapshot_acc_samples[ snapshot_acc_idx%(sizeof(snapshot_acc_samples)/sizeof(snapshot_acc_samples[0])) ] = (ulong)diff_tile( config, "snapin", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( GAUGE, SNAPIN, ACCOUNT_LOADED ) );
+      snapshot_acc_samples[ snapshot_acc_idx%(sizeof(snapshot_acc_samples)/sizeof(snapshot_acc_samples[0])) ] = diff_tile( config, "snapin", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( GAUGE, SNAPIN, ACCOUNT_LOADED ) );
       snapshot_acc_idx++;
-      snapshot_wr_samples[ snapshot_wr_idx%(sizeof(snapshot_wr_samples)/sizeof(snapshot_wr_samples[0])) ] = (ulong)diff_tile( config, "snapwr", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( GAUGE, SNAPWR, BYTES_WRITTEN ) );
+      snapshot_wr_samples[ snapshot_wr_idx%(sizeof(snapshot_wr_samples)/sizeof(snapshot_wr_samples[0])) ] = diff_tile( config, "snapwr", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( GAUGE, SNAPWR, BYTES_WRITTEN ) );
       snapshot_wr_idx++;
 
       /* Events */
-      events_sent_samples[ events_sent_samples_idx%(sizeof(events_sent_samples)/sizeof(events_sent_samples[0])) ] = (ulong)diff_tile( config, "event", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, EVENT, SENT ) );
+      events_sent_samples[ events_sent_samples_idx%(sizeof(events_sent_samples)/sizeof(events_sent_samples[0])) ] = diff_tile( config, "event", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, EVENT, SENT ) );
       events_sent_samples_idx++;
-      events_acked_samples[ events_acked_samples_idx%(sizeof(events_acked_samples)/sizeof(events_acked_samples[0])) ] = (ulong)diff_tile( config, "event", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, EVENT, ACKED ) );
+      events_acked_samples[ events_acked_samples_idx%(sizeof(events_acked_samples)/sizeof(events_acked_samples[0])) ] = diff_tile( config, "event", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, EVENT, ACKED ) );
       events_acked_samples_idx++;
-      event_bytes_written_samples[ event_bytes_written_samples_idx%(sizeof(event_bytes_written_samples)/sizeof(event_bytes_written_samples[0])) ] = (ulong)diff_tile( config, "event", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, EVENT, BYTES_WRITTEN ) );
+      event_bytes_written_samples[ event_bytes_written_samples_idx%(sizeof(event_bytes_written_samples)/sizeof(event_bytes_written_samples[0])) ] = diff_tile( config, "event", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, EVENT, BYTES_WRITTEN ) );
       event_bytes_written_samples_idx++;
-      event_bytes_read_samples[ event_bytes_read_samples_idx%(sizeof(event_bytes_read_samples)/sizeof(event_bytes_read_samples[0])) ] = (ulong)diff_tile( config, "event", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, EVENT, BYTES_READ ) );
+      event_bytes_read_samples[ event_bytes_read_samples_idx%(sizeof(event_bytes_read_samples)/sizeof(event_bytes_read_samples[0])) ] = diff_tile( config, "event", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, EVENT, BYTES_READ ) );
       event_bytes_read_samples_idx++;
 
       /* Accounts */
@@ -1684,17 +1689,17 @@ run( config_t const * config,
       sample_gossip( config, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, now );
 
       /* Repair server */
-      shreds_stored_sample[ shreds_stored_samples_idx%(sizeof(shreds_stored_sample)/sizeof(shreds_stored_sample[0])) ] = (ulong)diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( GAUGE, RSERVE, SHREDS_CURRENT ) );
+      shreds_stored_sample[ shreds_stored_samples_idx%(sizeof(shreds_stored_sample)/sizeof(shreds_stored_sample[0])) ] = diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( GAUGE, RSERVE, SHREDS_CURRENT ) );
       shreds_stored_samples_idx++;
 
-      rserve_rps_valid_samples[ rserve_rps_valid_samples_idx%(sizeof(rserve_rps_valid_samples)/sizeof(rserve_rps_valid_samples[0])) ] = (ulong)(
+      rserve_rps_valid_samples[ rserve_rps_valid_samples_idx%(sizeof(rserve_rps_valid_samples)/sizeof(rserve_rps_valid_samples[0])) ] =
           diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, RSERVE, SENT_RESPONSE_TYPES_PING ) ) +
           diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, RSERVE, SENT_RESPONSE_TYPES_WINDOW ) ) +
           diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, RSERVE, SENT_RESPONSE_TYPES_HIGHEST_WINDOW ) ) +
-          diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, RSERVE, SENT_RESPONSE_TYPES_ORPHAN ) ) );
+          diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, RSERVE, SENT_RESPONSE_TYPES_ORPHAN ) );
       rserve_rps_valid_samples_idx++;
 
-      rserve_rps_invalid_samples[ rserve_rps_invalid_samples_idx%(sizeof(rserve_rps_invalid_samples)/sizeof(rserve_rps_invalid_samples[0])) ] = (ulong)(
+      rserve_rps_invalid_samples[ rserve_rps_invalid_samples_idx%(sizeof(rserve_rps_invalid_samples)/sizeof(rserve_rps_invalid_samples[0])) ] =
           diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, RSERVE, MISSED_RESPONSE_TYPES_PING ) ) +
           diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, RSERVE, MISSED_RESPONSE_TYPES_WINDOW ) ) +
           diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, RSERVE, MISSED_RESPONSE_TYPES_HIGHEST_WINDOW ) ) +
@@ -1705,28 +1710,28 @@ run( config_t const * config,
           diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, RSERVE, FAILED_NOT_FOR_US ) ) +
           diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, RSERVE, FAILED_OUTDATED ) ) +
           diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, RSERVE, FAILED_PING_CACHE_LOOKUP ) ) +
-          diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, RSERVE, FAILED_INVALID_SHRED_INDEX ) ) );
+          diff_tile( config, "rserve", tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ, tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ, MIDX( COUNTER, RSERVE, FAILED_INVALID_SHRED_INDEX ) );
       {
         ulong slot = rserve_rps_invalid_samples_idx % (sizeof(rserve_rps_miss_samples)/sizeof(rserve_rps_miss_samples[0]));
         ulong const * prev = tiles+(1UL-last_snap)*tile_cnt*FD_METRICS_TOTAL_SZ;
         ulong const * cur  = tiles+last_snap*tile_cnt*FD_METRICS_TOTAL_SZ;
 
-        rserve_rps_miss_samples[ slot ] = (ulong)(
+        rserve_rps_miss_samples[ slot ] =
             diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, MISSED_RESPONSE_TYPES_PING ) ) +
             diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, MISSED_RESPONSE_TYPES_WINDOW ) ) +
             diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, MISSED_RESPONSE_TYPES_HIGHEST_WINDOW ) ) +
-            diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, MISSED_RESPONSE_TYPES_ORPHAN ) ) );
+            diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, MISSED_RESPONSE_TYPES_ORPHAN ) );
 
-        rserve_rps_sigvfy_samples[ slot ] = (ulong)diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, FAILED_SIGVERIFY ) );
+        rserve_rps_sigvfy_samples[ slot ] = diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, FAILED_SIGVERIFY ) );
 
-        rserve_rps_stale_samples[ slot ] = (ulong)diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, FAILED_OUTDATED ) );
+        rserve_rps_stale_samples[ slot ] = diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, FAILED_OUTDATED ) );
 
-        rserve_rps_other_rej_samples[ slot ] = (ulong)(
+        rserve_rps_other_rej_samples[ slot ] =
             diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, FAILED_OWN_KEY ) ) +
             diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, FAILED_INVALID_TOKEN ) ) +
             diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, FAILED_NOT_FOR_US ) ) +
             diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, FAILED_INVALID_SHRED_INDEX ) ) +
-            diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, FAILED_PING_CACHE_LOOKUP ) ) );
+            diff_tile( config, "rserve", prev, cur, MIDX( COUNTER, RSERVE, FAILED_PING_CACHE_LOOKUP ) );
       }
       rserve_rps_invalid_samples_idx++;
 
```
