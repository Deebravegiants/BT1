# [?] restore: reject out-of-bounds txnhash_offset

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-05-10
Source: https://github.com/firedancer-io/firedancer/commit/808b2e67f2685830a5d85efe251d29cee08494c5
Type: security-commit

## Details
restore: reject out-of-bounds txnhash_offset

Fixes a snapshot DoS issue caused by OOB txnhash_offset values

## Patch
### src/discof/restore/utils/fd_slot_delta_parser.c
```diff
@@ -149,6 +149,14 @@ state_validate( fd_slot_delta_parser_t * parser ) {
         return FD_SLOT_DELTA_PARSER_ADVANCE_ERROR_SLOT_IS_NOT_ROOT;
       }
       break;
+    case STATE_STATUS_TXN_IDX:
+      if( FD_UNLIKELY( parser->txnhash_offset>FD_SLOT_DELTA_MAX_TXNHASH_OFFSET ) ) {
+        FD_LOG_WARNING(( "slot delta validation failed: %s (%d)",
+                         fd_slot_delta_parser_advance_str( FD_SLOT_DELTA_PARSER_ADVANCE_ERROR_INVALID_TXNHASH_OFFSET ),
+                         FD_SLOT_DELTA_PARSER_ADVANCE_ERROR_INVALID_TXNHASH_OFFSET ));
+        return FD_SLOT_DELTA_PARSER_ADVANCE_ERROR_INVALID_TXNHASH_OFFSET;
+      }
+      break;
     default: break;
   }
 
```

### src/discof/restore/utils/fd_slot_delta_parser.h
```diff
@@ -16,6 +16,11 @@ typedef struct fd_sstxncache_entry fd_sstxncache_entry_t;
 
 #define FD_SLOT_DELTA_MAX_ENTRIES (300UL)
 
+/* status cache txn hashes are a 20 byte extract of the 32 byte txn
+   message hash.  The txnhash_offset specifies where it is sampled at.
+   Due to an Agave bug, the max offset is 11 bytes.  */
+#define FD_SLOT_DELTA_MAX_TXNHASH_OFFSET (11UL)
+
 struct fd_slot_entry {
   ulong slot;
 
@@ -87,6 +92,7 @@ fd_slot_delta_parser_init( fd_slot_delta_parser_t * parser );
    https://github.com/anza-xyz/agave/blob/v3.1.8/snapshots/src/error.rs#L132 */
 #define FD_SLOT_DELTA_PARSER_ADVANCE_ERROR_TOO_MANY_ENTRIES           (-3)
 #define FD_SLOT_DELTA_PARSER_ADVANCE_ERROR_EXCESS_DATA_IN_BUFFER      (-4)
+#define FD_SLOT_DELTA_PARSER_ADVANCE_ERROR_INVALID_TXNHASH_OFFSET     (-5)
 #define FD_SLOT_DELTA_PARSER_ADVANCE_AGAIN                            ( 0)
 #define FD_SLOT_DELTA_PARSER_ADVANCE_ENTRY                            ( 1)
 #define FD_SLOT_DELTA_PARSER_ADVANCE_GROUP                            ( 2)
@@ -99,6 +105,7 @@ fd_slot_delta_parser_advance_str( int err ) {
     case FD_SLOT_DELTA_PARSER_ADVANCE_ERROR_SLOT_HASH_MULTIPLE_ENTRIES: return "error_slot_hash_multiple_entries";
     case FD_SLOT_DELTA_PARSER_ADVANCE_ERROR_TOO_MANY_ENTRIES:           return "error_too_many_entries";
     case FD_SLOT_DELTA_PARSER_ADVANCE_ERROR_EXCESS_DATA_IN_BUFFER:      return "error_excess_data_in_buffer";
+    case FD_SLOT_DELTA_PARSER_ADVANCE_ERROR_INVALID_TXNHASH_OFFSET:     return "error_invalid_txnhash_offset";
     case FD_SLOT_DELTA_PARSER_ADVANCE_AGAIN:                            return "again";
     case FD_SLOT_DELTA_PARSER_ADVANCE_ENTRY:                            return "entry";
     case FD_SLOT_DELTA_PARSER_ADVANCE_GROUP:                            return "group";
```

### src/discof/restore/utils/test_slot_delta_parser.c
```diff
@@ -125,7 +125,7 @@ mock_one_input( uchar * input,
   p += 32UL;
 
   /* txn idx */
-  *(ulong *)p = 12345UL;
+  *(ulong *)p = FD_SLOT_DELTA_MAX_TXNHASH_OFFSET;
   p += sizeof(ulong);
 
   /* cache status len */
@@ -268,7 +268,7 @@ mock_slot_delta_input( uchar * input,
       fd_memcpy( p, blockhash, 32UL );
       p += 32UL;
 
-      *(ulong *)p = 12345UL; /* txn idx */
+      *(ulong *)p = FD_SLOT_DELTA_MAX_TXNHASH_OFFSET; /* txn idx */
       p += sizeof(ulong);
 
       *(ulong *)p = num_cache_statuses[j]; /* cache status len */
@@ -445,6 +445,23 @@ test_zero_slot_deltas( fd_slot_delta_parser_t * parser ) {
   FD_TEST( result->bytes_consumed==sizeof(input) );
 }
 
+static void
+test_invalid_txnhash_offset( fd_slot_delta_parser_t * parser ) {
+  uchar input[ 97UL ];
+  fd_slot_delta_parser_init( parser );
+  mock_one_input_with_error( input, sizeof(input), 1, 1000UL, MOCK_ERROR_TYPE_NONE, 0 );
+
+  uchar * p = input;
+  p += sizeof(ulong); /* slot deltas len */
+  p += sizeof(ulong); /* slot */
+  p += sizeof(uchar); /* is_root */
+  p += sizeof(ulong); /* status len */
+  p += 32UL;          /* blockhash */
+  *(ulong *)p = FD_SLOT_DELTA_MAX_TXNHASH_OFFSET + 1UL;
+
+  consume( parser, input, sizeof(input), entry_cb_no_err, 1, FD_SLOT_DELTA_PARSER_ADVANCE_ERROR_INVALID_TXNHASH_OFFSET );
+}
+
 static void
 test_too_many_entries( fd_slot_delta_parser_t * parser ) {
   uchar input[ 5125UL ];
@@ -490,6 +507,7 @@ int main( int     argc,
   test_zero_slot_deltas( slot_delta_parser );
   test_multiple_slot_deltas_no_entries( slot_delta_parser );
   test_duplicate_slots( slot_delta_parser );
+  test_invalid_txnhash_offset( slot_delta_parser );
   test_too_many_entries( slot_delta_parser );
 
   fd_wksp_free_laddr( fd_slot_delta_parser_delete( fd_slot_delta_parser_leave( slot_delta_parser ) ) );
```
