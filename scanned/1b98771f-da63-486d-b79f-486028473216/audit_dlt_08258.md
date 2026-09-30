# [?] accdb: fix sandbox escape

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-04-02
Source: https://github.com/firedancer-io/firedancer/commit/0771d43a9722637aba5c7cf84a6b7bb0b7e49177
Type: security-commit

## Details
accdb: fix sandbox escape

Fixes missing sandbox policies for accdb writes, which allowed
read-only accdb users to delete accounts.

Reported-by: Thomas Lambertz <thomas.lambertz@neodyme.io>

## Patch
### src/app/firedancer-dev/commands/backtest.c
```diff
@@ -491,9 +491,9 @@ backtest_topo( config_t * config ) {
   }
 
   if( vinyl_enabled ) {
-    fd_topob_vinyl_rq( topo, "replay", 0UL, "accdb_replay", "replay", 4UL, 1024UL, 1024UL );
+    fd_topob_vinyl_rq( topo, "replay", 0UL, "accdb_replay", "replay", 4UL, 1024UL, 1024UL, FD_VINYL_PERM_READ_WRITE );
     for( ulong i=0UL; i<execrp_tile_cnt; i++ ) {
-      fd_topob_vinyl_rq( topo, "execrp", i, "accdb_execrp", "execrp", 4UL, 1024UL, 1024UL );
+      fd_topob_vinyl_rq( topo, "execrp", i, "accdb_execrp", "execrp", 4UL, 1024UL, 1024UL, FD_VINYL_PERM_READ_WRITE );
     }
   }
 
```

### src/app/firedancer/topology.c
```diff
@@ -1368,18 +1368,18 @@ fd_topo_initialize( config_t * config ) {
   fd_pod_insert_int( topo->props, "sandbox", config->development.sandbox ? 1 : 0 );
 
   if( vinyl_enabled ) {
-    fd_topob_vinyl_rq( topo, "genesi", 0UL, "accdb_genesi", "genesi", 4UL, 1024UL, 1024UL );
-    fd_topob_vinyl_rq( topo, "replay", 0UL, "accdb_replay", "replay", 4UL, 1024UL, 1024UL );
+    fd_topob_vinyl_rq( topo, "genesi", 0UL, "accdb_genesi", "genesi", 4UL, 1024UL, 1024UL, FD_VINYL_PERM_READ_WRITE );
+    fd_topob_vinyl_rq( topo, "replay", 0UL, "accdb_replay", "replay", 4UL, 1024UL, 1024UL, FD_VINYL_PERM_READ_WRITE );
     for( ulong i=0UL; i<execrp_tile_cnt; i++ ) {
-      fd_topob_vinyl_rq( topo, "execrp", i, "accdb_execrp", "execrp", 4UL, 1024UL, 1024UL );
+      fd_topob_vinyl_rq( topo, "execrp", i, "accdb_execrp", "execrp", 4UL, 1024UL, 1024UL, FD_VINYL_PERM_READ_WRITE );
     }
     for( ulong i=0UL; i<execle_tile_cnt; i++ ) {
-      fd_topob_vinyl_rq( topo, "execle", i, "accdb_execle", "execle", 4UL, 1024UL, 1024UL );
+      fd_topob_vinyl_rq( topo, "execle", i, "accdb_execle", "execle", 4UL, 1024UL, 1024UL, FD_VINYL_PERM_READ_WRITE );
     }
-    fd_topob_vinyl_rq( topo, "tower", 0UL, "accdb_tower", "tower", 4UL, 128UL, 128UL );
-    FOR(resolv_tile_cnt) fd_topob_vinyl_rq( topo, "resolv", i, "accdb_resolv", "resolv", 4UL, 1UL, 1UL );
+    fd_topob_vinyl_rq( topo, "tower", 0UL, "accdb_tower", "tower", 4UL, 128UL, 128UL, FD_VINYL_PERM_READ_ONLY );
+    FOR(resolv_tile_cnt) fd_topob_vinyl_rq( topo, "resolv", i, "accdb_resolv", "resolv", 4UL, 1UL, 1UL, FD_VINYL_PERM_READ_ONLY );
     if( rpc_enabled ) {
-      fd_topob_vinyl_rq( topo, "rpc", 0UL, "accdb_rpc", "rpc", 4UL, 1UL, 1UL );
+      fd_topob_vinyl_rq( topo, "rpc", 0UL, "accdb_rpc", "rpc", 4UL, 1UL, 1UL, FD_VINYL_PERM_READ_ONLY );
     }
   }
 
```

### src/disco/topo/fd_topob_vinyl.h
```diff
@@ -7,6 +7,9 @@
 #include "fd_topob.h"
 #include "../../util/pod/fd_pod_format.h"
 
+#define FD_VINYL_PERM_READ_ONLY  0U
+#define FD_VINYL_PERM_READ_WRITE 1U
+
 FD_PROTOTYPES_BEGIN
 
 /* fd_topob_vinyl_client declares a new vinyl client and attaches it to
@@ -21,7 +24,8 @@ fd_topob_vinyl_rq( fd_topo_t *  topo,
                    char const * link_name,
                    ulong        req_batch_max,
                    ulong        req_batch_key_max,
-                   ulong        quota_max ) {
+                   ulong        quota_max,
+                   uint         vinyl_perm ) {
 
   /* Assumes there is only one vinyl tile in the topology */
   ulong accdb_tile_id;
@@ -41,6 +45,7 @@ fd_topob_vinyl_rq( fd_topo_t *  topo,
   FD_TEST( fd_pod_insertf_ulong( topo->props, req_batch_max, "obj.%lu.req_cnt",   rq_obj->id ) );
   FD_TEST( fd_pod_insertf_ulong( topo->props, rq_obj->id,    "obj.%lu.link_id",   rq_obj->id ) );
   FD_TEST( fd_pod_insertf_ulong( topo->props, quota_max,     "obj.%lu.quota_max", rq_obj->id ) );
+  FD_TEST( fd_pod_insertf_uint ( topo->props, vinyl_perm,    "obj.%lu.perm",      rq_obj->id ) );
 
   /* No database client uses the completion queue yet, but one is
      required to join a database client to the server. */
```

### src/discof/accdb/fd_accdb_tile.c
```diff
@@ -9,8 +9,8 @@
 
 #define _GNU_SOURCE
 #include "../../disco/topo/fd_topo.h"
+#include "../../disco/topo/fd_topob_vinyl.h"
 #include "../../disco/metrics/fd_metrics.h"
-#include "../../discof/restore/fd_snapct_tile.h"
 #include "../../vinyl/fd_vinyl.h"
 #include "../../vinyl/fd_vinyl_base.h"
 #include "../../vinyl/io/ur/fd_vinyl_io_ur.h"
@@ -47,6 +47,7 @@ struct fd_vinyl_client {
   ulong           laddr1;    /* ... and thus is in (laddr0,laddr1).  A zero gaddr maps to laddr NULL. */
   ulong           quota_rem; /* Num of remaining acquisitions this client is allowed on this vinyl instance */
   ulong           quota_max; /* Max quota */
+  uint            writable : 1;
 };
 
 typedef struct fd_vinyl_client fd_vinyl_client_t;
@@ -457,10 +458,12 @@ unprivileged_init( fd_topo_t *      topo,
     ulong quota_max       = fd_pod_queryf_ulong( topo->props, ULONG_MAX, "obj.%lu.quota_max",       rq_obj_id );
     ulong req_pool_obj_id = fd_pod_queryf_ulong( topo->props, ULONG_MAX, "obj.%lu.req_pool_obj_id", rq_obj_id );
     ulong cq_obj_id       = fd_pod_queryf_ulong( topo->props, ULONG_MAX, "obj.%lu.cq_obj_id",       rq_obj_id );
+    uint  rq_perm         = fd_pod_queryf_uint ( topo->props, UINT_MAX,  "obj.%lu.perm",            rq_obj_id );
     FD_TEST( link_id        !=ULONG_MAX );
     FD_TEST( quota_max      !=ULONG_MAX );
     FD_TEST( req_pool_obj_id!=ULONG_MAX );
     FD_TEST( cq_obj_id      !=ULONG_MAX );
+    FD_TEST( rq_perm==FD_VINYL_PERM_READ_ONLY || rq_perm==FD_VINYL_PERM_READ_WRITE );
 
     if( FD_UNLIKELY( burst_max > burst_free ) ) {
       FD_LOG_ERR(( "too large burst_max (increase FD_VINYL_REQ_MAX or decrease burst_max)" ));
@@ -498,7 +501,8 @@ unprivileged_init( fd_topo_t *      topo,
       .laddr0    = (ulong)join_info.shmem,
       .laddr1    = (ulong)join_info.shmem + join_info.page_cnt*join_info.page_sz,
       .quota_rem = quota_max,
-      .quota_max = quota_max
+      .quota_max = quota_max,
+      .writable  = rq_perm==FD_VINYL_PERM_READ_WRITE
     };
     ctx->client_cnt++;
 
@@ -844,6 +848,7 @@ before_credit( fd_vinyl_tile_t *   ctx,
     ulong  client_idx =        req->link_id; /* See note above about link_id / client_idx conversion */
     ulong  batch_cnt  = (ulong)req->batch_cnt;
     ulong  comp_gaddr =        req->comp_gaddr;
+    uint   req_flags  =        req->flags;
 
     fd_vinyl_client_t * client = ctx->_client + client_idx;
 
@@ -852,9 +857,26 @@ before_credit( fd_vinyl_tile_t *   ctx,
     ulong           client_laddr0 = client->laddr0;
     ulong           client_laddr1 = client->laddr1;
     ulong           quota_rem     = client->quota_rem;
+    _Bool           writable      = client->writable;
 
     FD_CRIT( quota_rem<=client->quota_max, "corruption detected" );
 
+    /* Permission checks */
+    if( !writable ) {
+      switch( req->type ) {
+      case FD_VINYL_REQ_TYPE_ACQUIRE:
+      case FD_VINYL_REQ_TYPE_RELEASE:
+        if( FD_UNLIKELY( fd_vinyl_req_flag_modify( req_flags ) ) ) {
+          FD_LOG_CRIT(( "sandbox violation: client with link_id=%lu attempted write operation (req_type=%d flags=%#x)",
+                        link_id, req->type, req_flags ));
+        }
+        break;
+      default:
+        FD_LOG_CRIT(( "sandbox violation: client with link_id=%lu attempted disallowed request type (req_type=%d)",
+                      link_id, req->type ));
+      }
+    }
+
     fd_vinyl_comp_t * comp = MAP_REQ_GADDR( comp_gaddr, fd_vinyl_comp_t, 1UL );
     if( FD_UNLIKELY( (!comp) & (!!comp_gaddr) ) ) {
       FD_LOG_CRIT(( "client with link_id=%lu requested completion at invalid gaddr %lu",
```
