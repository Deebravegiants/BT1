# [?] vinyl: fix bstream wraparound crash

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-04-02
Source: https://github.com/firedancer-io/firedancer/commit/22415747e770c03294073e3c261cac7ef1c86915
Type: security-commit

## Details
vinyl: fix bstream wraparound crash

Reported-by: Giorgi Arsenadze <gromji@osec.io>

## Patch
### src/vinyl/io/ur/fd_vinyl_io_ur_rd.c
```diff
@@ -366,7 +366,7 @@ rq_completion( fd_vinyl_io_ur_t * ur ) {
   uint * psz;
   if( FD_LIKELY( req_type==UR_REQ_READ ) ) {
     poff = &rd->head_off; psz = &rd->head_sz;
-  } else if( req_type==UR_REQ_WRITE ) {
+  } else if( req_type==UR_REQ_READ_TAIL ) {
     poff = &rd->tail_off; psz = &rd->tail_sz;
   } else {
     FD_LOG_CRIT(( "unexpected CQE (user_data=0x%016llx)", cqe->user_data ));
```

### src/vinyl/io/ur/test_vinyl_io_ur.c
```diff
@@ -203,6 +203,89 @@ main( int     argc,
 
   /* FIXME: TEST BSTREAM WRITE HELPERS */
 
+  FD_LOG_NOTICE(( "Testing wraparound async read" ));
+
+  {
+    fd_vinyl_io_ur_t * ur = (fd_vinyl_io_ur_t *)io;
+    ulong dev_sz = ur->dev_sz;
+
+    /* Fill up the device until seq_future % dev_sz is near the end,
+       leaving just one block of headroom before the wraparound point. */
+
+    ulong block_sz = FD_VINYL_BSTREAM_BLOCK_SZ;
+    while( (io->seq_future % dev_sz) < (dev_sz - 2*block_sz) ) {
+      ulong dev_free = dev_sz - (io->seq_future - io->seq_ancient);
+      if( dev_free < block_sz ) {
+        /* Need to free space */
+        fd_vinyl_io_forget( io, io->seq_present );
+        fd_vinyl_io_sync( io, FD_VINYL_IO_FLAG_BLOCKING );
+      }
+
+      fd_vinyl_bstream_block_t blk[1];
+      memset( blk, (int)((io->seq_future / block_sz) & 0xFFU), block_sz );
+      bcache_append( blk, block_sz );
+      fd_vinyl_io_append( io, blk, block_sz );
+      bcache_commit();
+      FD_TEST( !fd_vinyl_io_commit( io, FD_VINYL_IO_FLAG_BLOCKING ) );
+    }
+
+    /* Now seq_future % dev_sz is within 2 blocks of the device end.
+       Append 2 more blocks so the read will span the boundary. */
+
+    ulong dev_free = dev_sz - (io->seq_future - io->seq_ancient);
+    if( dev_free < 4*block_sz ) {
+      fd_vinyl_io_forget( io, io->seq_present );
+      fd_vinyl_io_sync( io, FD_VINYL_IO_FLAG_BLOCKING );
+    }
+
+    ulong read_seq = io->seq_future;
+    for( ulong i=0; i<4; i++ ) {
+      fd_vinyl_bstream_block_t blk[1];
+      memset( blk, (int)((0xA0UL+i) & 0xFFU), block_sz );
+      bcache_append( blk, block_sz );
+      fd_vinyl_io_append( io, blk, block_sz );
+    }
+    bcache_commit();
+    FD_TEST( !fd_vinyl_io_commit( io, FD_VINYL_IO_FLAG_BLOCKING ) );
+    bcache_sync();
+    FD_TEST( !fd_vinyl_io_sync( io, FD_VINYL_IO_FLAG_BLOCKING ) );
+
+    ulong read_sz = 4*block_sz;
+
+    /* Verify the read wraps around */
+    FD_TEST( (read_seq % dev_sz) + read_sz > dev_sz );
+
+    /* Re-init the io backend so that seq_cache resets to seq_present,
+       forcing all reads through io_uring instead of the write-back
+       cache.  Without this, wb_read serves the data from cache and the
+       io_uring wraparound code path is never exercised. */
+
+    FD_TEST( fd_vinyl_io_fini( io )==mem );
+    io = fd_vinyl_io_ur_init( mem, spad_max, fd, ring );
+    FD_TEST( io );
+
+    /* Do an async read across the wraparound boundary */
+    uchar ref[ 4*FD_VINYL_BSTREAM_BLOCK_SZ ] __attribute__((aligned(FD_VINYL_BSTREAM_BLOCK_SZ)));
+    uchar tst[ 4*FD_VINYL_BSTREAM_BLOCK_SZ ] __attribute__((aligned(FD_VINYL_BSTREAM_BLOCK_SZ)));
+
+    bcache_read( read_seq, ref, read_sz );
+    memset( tst, 0, read_sz );
+
+    fd_vinyl_io_rd_t rd[1];
+    rd->ctx = 0xDEADBEEFUL;
+    rd->seq = read_seq;
+    rd->dst = tst;
+    rd->sz  = read_sz;
+
+    fd_vinyl_io_read( io, rd );
+
+    fd_vinyl_io_rd_t * completed;
+    FD_TEST( !fd_vinyl_io_poll( io, &completed, FD_VINYL_IO_FLAG_BLOCKING ) );
+    FD_TEST( completed==rd );
+    FD_TEST( rd->ctx==0xDEADBEEFUL );
+    FD_TEST( !memcmp( ref, tst, read_sz ) );
+  }
+
   FD_LOG_NOTICE(( "Testing destruction" ));
 
   fd_vinyl_bstream_block_t block[1];
```
