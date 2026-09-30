# [?] agave: fix ulong overflow bug

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-08-01
Source: https://github.com/firedancer-io/firedancer/commit/48c63fb798ebb0de62488365728c2938a09dcb16
Type: security-commit

## Details
agave: fix ulong overflow bug

## Patch
### src/app/fdctl/commands/run_agave.c
```diff
@@ -181,7 +181,12 @@ agave_boot( config_t const * config ) {
     }
     ADDU( "--unified-scheduler-handler-threads", config->frankendancer.layout.agave_unified_scheduler_handler_threads );
   } else {
-    ulong num_threads = fd_ulong_max( config->topo.agave_affinity_cnt-4UL, fd_ulong_min( config->topo.agave_affinity_cnt, 4UL ) );
+    //          agave_affinity_cnt >= 8  =>  agave_affinity_cnt - 4
+    //     4 <= agave_affinity_cnt <  8  =>  4
+    //          agave_affinity_cnt <  4  =>  agave_affinity_cnt
+    ulong num_threads = fd_ulong_if( config->topo.agave_affinity_cnt>=4UL,
+                                     fd_ulong_if( config->topo.agave_affinity_cnt>=8, config->topo.agave_affinity_cnt-4UL, 4UL ),
+                                     config->topo.agave_affinity_cnt );
     ADDU( "--unified-scheduler-handler-threads", (uint)num_threads );
   }
 
```
