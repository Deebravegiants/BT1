# [?] restore: fix struct overflow parsing ns_per_slot

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-09-07
Source: https://github.com/firedancer-io/firedancer/commit/beec72d1e0b9cf490648355e6775af42724d1910
Type: security-commit

## Details
restore: fix struct overflow parsing ns_per_slot

## Patch
### src/discof/restore/utils/fd_ssmanifest_parser.c
```diff
@@ -392,6 +392,7 @@ struct fd_ssmanifest_parser_private {
   uchar   option;
   uint    variant;
   double  warmup_cooldown_rate;
+  uchar   ns_per_slot[ 16UL ];
 
   ulong   idx1;
   ulong   idx2;
@@ -832,7 +833,7 @@ state_dst( fd_ssmanifest_parser_t * parser ) {
     case STATE_HASHES_PER_TICK_OPTION:                                                                        return &parser->option;
     case STATE_HASHES_PER_TICK:                                                                               return (uchar*)&manifest->hashes_per_tick;
     case STATE_TICKS_PER_SLOT:                                                                                return (uchar*)&manifest->ticks_per_slot;
-    case STATE_NS_PER_SLOT:                                                                                   return (uchar*)&manifest->ns_per_slot;
+    case STATE_NS_PER_SLOT:                                                                                   return parser->ns_per_slot;
     case STATE_GENSIS_CREATION_TIME:                                                                          return (uchar*)&manifest->creation_time_seconds;
     case STATE_SLOTS_PER_YEAR:                                                                                return (uchar*)&manifest->slots_per_year;
     case STATE_ACCOUNTS_DATA_LEN:                                                                             return NULL;
@@ -1264,6 +1265,13 @@ state_validate( fd_ssmanifest_parser_t * parser ) {
       }
       break;
     }
+    case STATE_NS_PER_SLOT: {
+      if( FD_UNLIKELY( fd_ulong_load_8( parser->ns_per_slot+8UL ) ) ) {
+        FD_LOG_WARNING(( "ns_per_slot does not fit in 64 bits" ));
+        return -1;
+      }
+      break;
+    }
     case STATE_BANK_INCREMENTAL_SNAPSHOT_PERSISTENCE_OPTION: {
       if( FD_UNLIKELY( parser->option>1 ) ) {
         FD_LOG_WARNING(( "invalid bank_incremental_snapshot_persistence option %d", parser->option ));
@@ -1720,6 +1728,10 @@ state_process( fd_ssmanifest_parser_t * parser ) {
     return -1;
   }
 
+  if( FD_UNLIKELY( parser->state==STATE_NS_PER_SLOT ) ) {
+    manifest->ns_per_slot = fd_ulong_load_8( parser->ns_per_slot );
+  }
+
   if( FD_UNLIKELY( parser->state==STATE_EPOCH_SCHEDULE_FIRST_NORMAL_SLOT ) ) {
     fd_epoch_schedule_t epoch_schedule = (fd_epoch_schedule_t){
       .slots_per_epoch             = manifest->epoch_schedule_params.slots_per_epoch,
```
