# [?] net: fix startup race condition

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-07-30
Source: https://github.com/firedancer-io/firedancer/commit/ed24014a35ae29ac7775415d2a6716079b730aeb
Type: security-commit

## Details
net: fix startup race condition

## Patch
### src/disco/net/xdp/fd_xdp_tile.c
```diff
@@ -233,11 +233,11 @@ typedef struct {
   fd_netlink_neigh4_solicit_link_t neigh4_solicit[1];
 
   /* Netdev table */
-  fd_netdev_tbl_join_t netdev_tbl_handle; // handle to the netdev table itself
-  fd_dbl_buf_t       * netdev_dbl_handle; // handle to the double buffer
-  uchar              * netdev_buf;        // local buf to copy in the netdev table
-  ulong                netdev_buf_sz;     // size of netdev_buf above
-  int                  has_gre_interface; // netdev table has a GRE interface entry
+  fd_dbl_buf_t *       netdev_dbl_buf;    /* remote copy of device table */
+  uchar *              netdev_buf;        /* local copy of device table */
+  ulong                netdev_buf_sz;
+  fd_netdev_tbl_join_t netdev_tbl;        /* join to local copy of device table */
+  int                  has_gre_interface; /* enable GRE support? */
 
   struct {
     ulong rx_pkt_cnt;
@@ -371,35 +371,32 @@ net_is_fatal_xdp_error( int err ) {
 
 static void
 net_load_netdev_tbl( fd_net_ctx_t * ctx ) {
-  /* Copy from double buffer */
-  if( FD_UNLIKELY( !fd_dbl_buf_read( ctx->netdev_dbl_handle, ctx->netdev_buf_sz, ctx->netdev_buf, NULL ) ) )  FD_LOG_ERR(("netdev table load failed"));
+  /* Copy netdev table from netlink tile.  This could fail briefly
+     during startup if the netlink tile is late to start up. */
+  if( FD_UNLIKELY( !fd_dbl_buf_read( ctx->netdev_dbl_buf, ctx->netdev_buf_sz, ctx->netdev_buf, NULL ) ) ) return;
 
-  /* Recalculate the join handler to netdeb buf */
-  if( FD_UNLIKELY( !fd_netdev_tbl_join( &ctx->netdev_tbl_handle, ctx->netdev_buf ) ) ) FD_LOG_ERR(("netdev table join failed"));
+  /* Join local copy */
+  if( FD_UNLIKELY( !fd_netdev_tbl_join( &ctx->netdev_dbl_buf, ctx->netdev_buf ) ) ) FD_LOG_ERR(("netdev table join failed"));
 }
 
 /* Query the netdev table. Return a fd_netdev_t pointer to the net device of the
 interface specified by if_idx. Null if the if_idx is invalid */
 
 static fd_netdev_t *
-net_query_netdev_tbl( fd_net_ctx_t *ctx,
-                      uint if_idx ) {
+net_query_netdev_tbl( fd_net_ctx_t * ctx,
+                      uint           if_idx ) {
   /* dev_tbl is one-indexed */
-  if( if_idx>ctx->netdev_tbl_handle.hdr->dev_cnt ) {
-    FD_LOG_NOTICE(( "interface idx invalid (%u). dev_cnt (%u)", if_idx, ctx->netdev_tbl_handle.hdr->dev_cnt ));
-    return NULL;
-  }
-
-  return &ctx->netdev_tbl_handle.dev_tbl[if_idx];
+  if( if_idx>ctx->netdev_tbl.hdr->dev_cnt ) return NULL;
+  return &ctx->netdev_tbl.dev_tbl[ if_idx ];
 }
 
 /* Iterates the netdev table and returns 1 if a GRE interface exists, 0 otherwise.
    Only called in privileged_init and during_housekeeping */
 
 static int
 net_check_gre_interface_exists( fd_net_ctx_t * ctx ) {
-  fd_netdev_t * dev_tbl = ctx->netdev_tbl_handle.dev_tbl;
-  ushort        dev_cnt = ctx->netdev_tbl_handle.hdr->dev_cnt;
+  fd_netdev_t * dev_tbl = ctx->netdev_tbl.dev_tbl;
+  ushort        dev_cnt = ctx->netdev_tbl.hdr->dev_cnt;
 
   for( ushort if_idx = 0; if_idx<dev_cnt; if_idx++ ) {
     if( dev_tbl[if_idx].dev_type==ARPHRD_IPGRE ) return 1;
@@ -538,7 +535,7 @@ during_housekeeping( fd_net_ctx_t * ctx ) {
 static int
 net_tx_route( fd_net_ctx_t * ctx,
               uint           dst_ip,
-              uint         * is_gre_inf ) {
+              uint *         is_gre_inf ) {
 
   /* Route lookup */
 
@@ -1352,6 +1349,30 @@ privileged_init( fd_topo_t *      topo,
     FD_LOG_ERR(( "scratch overflow %lu %lu %lu", scratch_top - (ulong)scratch - scratch_footprint( tile ), scratch_top, (ulong)scratch + scratch_footprint( tile ) ));
 }
 
+/* init_device_table joins the net tile to the netlink tile's device
+   table.  The device table is very frequently read, and rarely updated.
+   Therefore, the net tile keeps a local copy of the device table in
+   scratch memory.  This table is periodically copied over from the
+   netlink tile via a double buffer (netdev_dbl_buf).
+
+   On startup, the netlink tile might not have produced its initial
+   device table.  Therefore, initialize the local copy to an empty
+   table. */
+
+static void
+init_device_table( fd_net_ctx_t * ctx,
+                   void *         netdev_dbl_buf ) {
+
+  /* Join remote double buffer containing device table updates */
+  ctx->netdev_dbl_buf = fd_dbl_buf_join( netdev_dbl_buf );
+  if( FD_UNLIKELY( !ctx->netdev_dbl_buf ) ) FD_LOG_ERR(( "fd_dbl_buf_join failed" ));
+  ctx->netdev_buf_sz  = fd_netdev_tbl_footprint( NETDEV_MAX, BOND_MASTER_MAX );
+
+  /* Create temporary empty device table during startup */
+  FD_TEST( fd_netdev_tbl_join( &ctx->netdev_tbl, fd_netdev_tbl_new( ctx->netdev_buf, 1, 1 ) ) );
+
+}
+
 FD_FN_UNUSED static void
 unprivileged_init( fd_topo_t *      topo,
                    fd_topo_tile_t * tile ) {
@@ -1469,16 +1490,7 @@ unprivileged_init( fd_topo_t *      topo,
     FD_LOG_ERR(( "fd_neigh4_hmap_join failed" ));
   }
 
-  /* Allocate and join netdev buffer */
-  ctx->netdev_dbl_handle       = fd_dbl_buf_join( fd_topo_obj_laddr( topo, tile->xdp.netdev_dbl_buf_obj_id ) );
-  if( FD_UNLIKELY( ctx->netdev_dbl_handle==NULL ) ) FD_LOG_ERR(( "fd_dbl_buf_join failed" ))  ;
-  ctx->netdev_buf_sz           = fd_netdev_tbl_footprint( NETDEV_MAX, BOND_MASTER_MAX );
-
-  /* Load the netdev table for the first time */
-  net_load_netdev_tbl( ctx );
-
-  /* Loop through netdev table to find if GRE interface exists */
-  ctx->has_gre_interface = net_check_gre_interface_exists( ctx );
+  init_device_table( ctx, fd_topo_obj_laddr( topo, tile->xdp.netdev_dbl_buf_obj_id ) );
 
   /* Initialize TX free ring */
 
```

### src/disco/net/xdp/test_xdp_tile.c
```diff
@@ -140,35 +140,35 @@ setup_routing_table( fd_net_ctx_t * ctx,
 static void
 setup_netdev_table( fd_net_ctx_t * ctx ) {
   /* GRE interfaces */
-  ctx->netdev_tbl_handle.dev_tbl[IF_IDX_GRE0] = (fd_netdev_t) {
+  ctx->netdev_tbl.dev_tbl[IF_IDX_GRE0] = (fd_netdev_t) {
     .if_idx = IF_IDX_GRE0,
     .dev_type = ARPHRD_IPGRE,
     .gre_dst_ip = gre0_outer_dst_ip,
     .gre_src_ip = gre0_outer_src_ip
   };
-  ctx->netdev_tbl_handle.dev_tbl[IF_IDX_GRE1] = (fd_netdev_t) {
+  ctx->netdev_tbl.dev_tbl[IF_IDX_GRE1] = (fd_netdev_t) {
     .if_idx = IF_IDX_GRE1,
     .dev_type = ARPHRD_IPGRE,
     .gre_dst_ip = gre1_outer_dst_ip,
   };
   /* Eth0 interface */
-  ctx->netdev_tbl_handle.dev_tbl[IF_IDX_ETH0] = (fd_netdev_t) {
+  ctx->netdev_tbl.dev_tbl[IF_IDX_ETH0] = (fd_netdev_t) {
     .if_idx = IF_IDX_ETH0,
     .dev_type = ARPHRD_ETHER,
   };
   /* Eth1 interface */
-  ctx->netdev_tbl_handle.dev_tbl[IF_IDX_ETH1] = (fd_netdev_t) {
+  ctx->netdev_tbl.dev_tbl[IF_IDX_ETH1] = (fd_netdev_t) {
     .if_idx = IF_IDX_ETH1,
     .dev_type = ARPHRD_ETHER,
   };
   /* Lo interface */
-  ctx->netdev_tbl_handle.dev_tbl[IF_IDX_LO] = (fd_netdev_t) {
+  ctx->netdev_tbl.dev_tbl[IF_IDX_LO] = (fd_netdev_t) {
     .if_idx = IF_IDX_LO,
     .dev_type = ARPHRD_LOOPBACK,
   };
-  fd_memcpy( (fd_netdev_t *)ctx->netdev_tbl_handle.dev_tbl[IF_IDX_ETH0].mac_addr, eth0_src_mac_addr, 6 );
-  fd_memcpy( (fd_netdev_t *)ctx->netdev_tbl_handle.dev_tbl[IF_IDX_ETH1].mac_addr, eth1_src_mac_addr, 6 );
-  ctx->netdev_tbl_handle.hdr->dev_cnt = IF_IDX_GRE1 + 1;
+  fd_memcpy( (fd_netdev_t *)ctx->netdev_tbl.dev_tbl[IF_IDX_ETH0].mac_addr, eth0_src_mac_addr, 6 );
+  fd_memcpy( (fd_netdev_t *)ctx->netdev_tbl.dev_tbl[IF_IDX_ETH1].mac_addr, eth1_src_mac_addr, 6 );
+  ctx->netdev_tbl.hdr->dev_cnt = IF_IDX_GRE1 + 1;
 }
 
 
@@ -299,6 +299,8 @@ main( int     argc,
   ctx->free_tx.depth  = topo_tile->xdp.free_ring_depth;
   ctx->netdev_buf     = FD_SCRATCH_ALLOC_APPEND( l, fd_netdev_tbl_align(), ctx->netdev_buf_sz );
 
+  init_device_table( ctx, netdev_dbl_buf_mem );
+
   FD_TEST( fd_topo_obj_laddr( topo, topo_tile->net.umem_dcache_obj_id )==umem_dcache_mem );
   void * const umem_dcache         = fd_dcache_join( umem_dcache_mem );
   FD_TEST( umem_dcache );
@@ -386,6 +388,11 @@ main( int     argc,
   /* Routing table */
   setup_routing_table( ctx, fib4_local_mem, fib4_main_mem );
 
+  /* Ensure initial (fake) device table is valid */
+  FD_TEST( net_check_gre_interface_exists( ctx )==0 );
+  uint is_gre_inf = 0U;
+  FD_TEST( net_tx_route( ctx, FD_IP4_ADDR( 1,1,1,1 ), &is_gre_inf )==0 );
+
   /* Neighbor table */
   add_neighbor( neigh4_hmap, gre0_outer_dst_ip, eth0_dst_mac_addr[0], eth0_dst_mac_addr[1], eth0_dst_mac_addr[2], eth0_dst_mac_addr[3], eth0_dst_mac_addr[4], eth0_dst_mac_addr[5] );
   add_neighbor( neigh4_hmap, gre1_outer_dst_ip, eth1_dst_mac_addr[0], eth1_dst_mac_addr[1], eth1_dst_mac_addr[2], eth1_dst_mac_addr[3], eth1_dst_mac_addr[4], eth1_dst_mac_addr[5] );
@@ -397,15 +404,15 @@ main( int     argc,
 
   /* Netdev table */
   FD_TEST( fd_topo_obj_laddr( topo, topo_tile->xdp.netdev_dbl_buf_obj_id )==netdev_dbl_buf_mem );
-  ctx->netdev_dbl_handle = fd_dbl_buf_join( netdev_dbl_buf_mem );
-  ctx->netdev_buf_sz     = fd_netdev_tbl_footprint( NETDEV_MAX, BOND_MASTER_MAX );
-  ctx->netdev_buf        = FD_SCRATCH_ALLOC_APPEND( l, fd_netdev_tbl_align(), ctx->netdev_buf_sz );
+  ctx->netdev_dbl_buf = fd_dbl_buf_join( netdev_dbl_buf_mem );
+  ctx->netdev_buf_sz  = fd_netdev_tbl_footprint( NETDEV_MAX, BOND_MASTER_MAX );
+  ctx->netdev_buf     = FD_SCRATCH_ALLOC_APPEND( l, fd_netdev_tbl_align(), ctx->netdev_buf_sz );
   fd_netdev_tbl_new( ctx->netdev_buf, NETDEV_MAX, BOND_MASTER_MAX );
-  FD_TEST( fd_netdev_tbl_join( &ctx->netdev_tbl_handle, ctx->netdev_buf ) );
+  FD_TEST( fd_netdev_tbl_join( &ctx->netdev_tbl, ctx->netdev_buf ) );
   setup_netdev_table( ctx );
   ctx->has_gre_interface = 1;
 
-  /* ctx->in*/
+  /* ctx->in */
   ctx->in[ 0 ].mem    = fd_wksp_containing( app_tx_dcache_mem );
   ctx->in[ 0 ].chunk0 = tx_chunk0;
   ctx->in[ 0 ].wmark  = tx_wmark;
```
