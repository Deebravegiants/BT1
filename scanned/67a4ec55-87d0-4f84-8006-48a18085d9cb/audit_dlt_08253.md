# [?] gossip: fix ts overflow (#9718)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-05-12
Source: https://github.com/firedancer-io/firedancer/commit/9867270ee691b7c9922aae4ff65b06dc711c3b26
Type: security-commit

## Details
gossip: fix ts overflow (#9718)

## Patch
### src/discof/gossip/fd_gossvf_tile.c
```diff
@@ -787,26 +787,26 @@ handle_net( fd_gossvf_tile_ctx_t * ctx,
     if( FD_UNLIKELY( !memcmp( message->pull_request->contact_info->origin, ctx->identity_pubkey, 32UL ) ) ) return FD_METRICS_ENUM_GOSSVF_MESSAGE_OUTCOME_V_DROPPED_PULL_REQUEST_LOOPBACK_IDX;
     if( FD_UNLIKELY( message->pull_request->crds_filter->mask_bits>=64U ) ) return FD_METRICS_ENUM_GOSSVF_MESSAGE_OUTCOME_V_DROPPED_PULL_REQUEST_MASK_BITS_IDX;
 
-    long clamp_wallclock_lower_nanos = now-15L*1000L*1000L*1000L;
-    long clamp_wallclock_upper_nanos = now+15L*1000L*1000L*1000L;
-    if( FD_UNLIKELY( FD_MILLI_TO_NANOSEC( message->pull_request->contact_info->wallclock )<clamp_wallclock_lower_nanos ||
-                     FD_MILLI_TO_NANOSEC( message->pull_request->contact_info->wallclock )>clamp_wallclock_upper_nanos ) ) return FD_METRICS_ENUM_GOSSVF_MESSAGE_OUTCOME_V_DROPPED_PULL_REQUEST_WALLCLOCK_IDX;
+    ulong clamp_wallclock_lower_millis = (ulong)(FD_NANOSEC_TO_MILLI( now )-15L*1000L);
+    ulong clamp_wallclock_upper_millis = (ulong)(FD_NANOSEC_TO_MILLI( now )+15L*1000L);
+    if( FD_UNLIKELY( message->pull_request->contact_info->wallclock<clamp_wallclock_lower_millis ||
+                     message->pull_request->contact_info->wallclock>clamp_wallclock_upper_millis ) ) return FD_METRICS_ENUM_GOSSVF_MESSAGE_OUTCOME_V_DROPPED_PULL_REQUEST_WALLCLOCK_IDX;
   }
 
   if( FD_UNLIKELY( message->tag==FD_GOSSIP_MESSAGE_PRUNE ) ) {
     if( FD_UNLIKELY( !!memcmp( message->prune->destination, ctx->identity_pubkey, 32UL ) ) ) return FD_METRICS_ENUM_GOSSVF_MESSAGE_OUTCOME_V_DROPPED_PRUNE_DESTINATION_IDX;
     /* Agave uses a window of 500ms here, rather than 1s, but it's too
        narrow in production and causes us to throw away a lot of prunes
        that are actually valid and useful. */
-    if( FD_UNLIKELY( now-1000L*1000L*1000L>FD_MILLI_TO_NANOSEC( message->prune->wallclock ) ) ) return FD_METRICS_ENUM_GOSSVF_MESSAGE_OUTCOME_V_DROPPED_PRUNE_WALLCLOCK_IDX;
+    if( FD_UNLIKELY( (ulong)(FD_NANOSEC_TO_MILLI( now )-1000L)>message->prune->wallclock ) ) return FD_METRICS_ENUM_GOSSVF_MESSAGE_OUTCOME_V_DROPPED_PRUNE_WALLCLOCK_IDX;
   }
 
   if( FD_LIKELY( message->tag==FD_GOSSIP_MESSAGE_PUSH ) ) {
     ulong i = 0UL;
     while( i<message->push->values_len ) {
       fd_gossip_value_t const * value = &message->push->values[ i ];
-      if( FD_UNLIKELY( FD_MILLI_TO_NANOSEC( value->wallclock )<now-15L*1000L*1000L*1000L ||
-                       FD_MILLI_TO_NANOSEC( value->wallclock )>now+15L*1000L*1000L*1000L ) ) {
+      if( FD_UNLIKELY( value->wallclock<(ulong)(FD_NANOSEC_TO_MILLI( now )-15L*1000L) ||
+                       value->wallclock>(ulong)(FD_NANOSEC_TO_MILLI( now )+15L*1000L) ) ) {
         ctx->metrics.crds_rx[ FD_METRICS_ENUM_GOSSVF_CRDS_OUTCOME_V_DROPPED_PUSH_WALLCLOCK_IDX ]++;
         ctx->metrics.crds_rx_bytes[ FD_METRICS_ENUM_GOSSVF_CRDS_OUTCOME_V_DROPPED_PUSH_WALLCLOCK_IDX ] += value->length;
         message->push->values[ i ] = message->push->values[ message->push->values_len-1UL ];
@@ -837,7 +837,7 @@ handle_net( fd_gossvf_tile_ctx_t * ctx,
         else                                   accept_after_nanos = now-432000L*400L*1000L*1000L;
       }
 
-      if( FD_UNLIKELY( accept_after_nanos>FD_MILLI_TO_NANOSEC( value->wallclock ) ) ) {
+      if( FD_UNLIKELY( (ulong)(FD_NANOSEC_TO_MILLI( accept_after_nanos ))>value->wallclock ) ) {
         peer_t const * origin_peer = peer_map_ele_query_const( ctx->peer_map, (fd_pubkey_t const *)value->origin, NULL, ctx->peers );
         if( FD_UNLIKELY( !origin_peer ) ) {
           ctx->metrics.crds_rx[ FD_METRICS_ENUM_GOSSVF_CRDS_OUTCOME_V_DROPPED_PULL_RESPONSE_WALLCLOCK_IDX ]++;
```
