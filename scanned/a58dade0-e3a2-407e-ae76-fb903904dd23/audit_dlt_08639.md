# [?] Merge pull request #17468 from MinaProtocol/lyh/fix-lmdb-deadlock

## Summary
Severity: Unknown
Chain: Mina
Component: MinaProtocol/mina
Published: 2025-07-07
Source: https://github.com/MinaProtocol/mina/commit/de90383687136796a58e22ea41b3a79370b7a269
Type: security-commit

## Details
Merge pull request #17468 from MinaProtocol/lyh/fix-lmdb-deadlock

Fix LMDB deadlock by not accessing LMDB in GC interrupt

## Patch
### changes/17468.md
```diff
@@ -0,0 +1 @@
+Fixed a bug that's blocking release 3.1.2: In GC interrupt, hooks into LMDB causes double lock requiring.
```

### src/lib/disk_cache/lmdb/disk_cache.ml
```diff
@@ -16,29 +16,63 @@ module Make (Data : Binable.S) = struct
 
   module Rw = Read_write (F)
 
-  type t = { env : Rw.t; db : Rw.holder; counter : int ref }
+  type t =
+    { env : Rw.t
+    ; db : Rw.holder
+    ; counter : int ref
+    ; logger : Logger.t
+    ; garbage : int Hash_set.t
+          (** A list of ids that are no longer reachable from OCaml's side *)
+    }
+
+  (** How big can the above hashset be before we do a cleanup *)
+  let garbage_size_limit = 512
 
   let initialize path ~logger =
     Async.Deferred.Result.map (Disk_cache_utils.initialize_dir path ~logger)
       ~f:(fun path ->
         let env, db = Rw.create path in
-        { env; db; counter = ref 0 } )
+        { env
+        ; db
+        ; counter = ref 0
+        ; logger
+        ; garbage = Hash_set.create (module Int)
+        } )
 
   type id = { idx : int }
 
-  let get ({ env; db; _ } : t) ({ idx } : id) : Data.t =
+  let get ({ env; db; logger; _ } : t) ({ idx } : id) : Data.t =
+    [%log debug] "Getting data at %d in LMDB cache" idx
+      ~metadata:[ ("index", `Int idx) ] ;
     Rw.get ~env db idx |> Option.value_exn
 
-  let put ({ env; db; counter } : t) (x : Data.t) : id =
+  let put ({ env; db; counter; logger; garbage } : t) (x : Data.t) : id =
+    (* TODO: we may reuse IDs by pulling them from the `garbage` hash set *)
     let idx = !counter in
     incr counter ;
     let res = { idx } in
     (* When this reference is GC'd, delete the file. *)
-    Gc.Expert.add_finalizer_last_exn res (fun () -> Rw.remove ~env db idx) ;
+    Gc.Expert.add_finalizer_last_exn res (fun () ->
+        (* The actual deletion is delayed, as GC maybe triggered in LMDB's
+           critical section. LMDB critical section then will be re-entered if
+           it's invoked directly in a GC hook.
+           This causes mutex double-acquiring and node freezes. *)
+        [%log spam] "Data at %d is GCed, marking as garbage" idx
+          ~metadata:[ ("index", `Int idx) ] ;
+        Hash_set.add garbage idx ) ;
+    if Hash_set.length garbage >= garbage_size_limit then (
+      Hash_set.iter garbage ~f:(fun to_remove ->
+          [%log spam] "Instructing LMDB to remove garbage at index %d" to_remove
+            ~metadata:[ ("index", `Int to_remove) ] ;
+          Rw.remove ~env db to_remove ) ;
+      Hash_set.clear garbage ) ;
     Rw.set ~env db idx x ;
     res
 
-  let iteri ({ env; db; _ } : t) ~f = Rw.iter ~env db ~f
+  let iteri ({ env; db; logger; _ } : t) ~f =
+    Rw.iter ~env db ~f:(fun k v ->
+        [%log spam] "Iterating at index %d" k ~metadata:[ ("index", `Int k) ] ;
+        f k v )
 
   let count ({ env; db; _ } : t) =
     let sum = ref 0 in
@@ -52,7 +86,7 @@ let%test_module "disk_cache lmdb" =
   ( module struct
     include Disk_cache_test_lib.Make_extended (Make)
 
-    let%test_unit "remove data on gc" = remove_data_on_gc ()
+    let%test_unit "remove data on gc" = remove_data_on_gc ~gc_strict:false ()
 
     let%test_unit "simple read/write (with iteration)" =
       simple_write_with_iteration ()
```

### src/lib/disk_cache/lmdb/dune
```diff
@@ -11,7 +11,7 @@
   disk_cache.utils
   disk_cache.test_lib)
  (preprocess
-  (pps ppx_version ppx_jane))
+  (pps ppx_version ppx_jane ppx_mina))
  (inline_tests
   (flags -verbose -show-counts))
  (instrumentation
```

### src/lib/disk_cache/test/test_lmdb_deadlock.ml
```diff
@@ -9,10 +9,7 @@ let () =
           (module Disk_cache)
       in
       match res with
-      | `Timeout ->
-          printf
-            "It is expected that LMDB cache times out for now. This should be \
-             fixed." ;
-          Deferred.unit
       | `Success ->
-          failwith "The process should time out" )
+          printf "Success" ; Deferred.unit
+      | `Timeout ->
+          failwith "The process should not time out" )
```

### src/lib/disk_cache/test_lib/disk_cache_test_lib.ml
```diff
@@ -23,7 +23,11 @@ module type S = sig
 
   val initialization_special_cases : unit -> unit
 
-  val remove_data_on_gc : unit -> unit
+  (** [remove_data_on_gc ?gc_strict ())] test behavior of cache on GC.
+      If [gc_strict] is set to [false], then we won't check if the cache is
+      empty after GC.
+   *)
+  val remove_data_on_gc : ?gc_strict:bool -> unit -> unit
 end
 
 module type S_extended = sig
@@ -77,7 +81,7 @@ module Make_impl (Cache : Disk_cache_intf.S_with_count with module Data := Mock)
     File_system.with_temp_dir "disk_cache"
       ~f:(simple_write_impl ?additional_checks)
 
-  let remove_data_on_gc_impl tmp_dir =
+  let remove_data_on_gc_impl ~gc_strict tmp_dir =
     let%map cache = initialize_cache_or_fail tmp_dir ~logger in
 
     let proof = Mock.{ proof = "dummy" } in
@@ -91,16 +95,16 @@ module Make_impl (Cache : Disk_cache_intf.S_with_count with module Data := Mock)
      [%test_eq: string] proof.proof proof_from_cache.proof
        ~message:"invalid proof from cache" ) ;
 
-    Gc.compact () ;
+    if gc_strict then (
+      Gc.compact () ;
+      [%test_eq: int] (Cache.count cache) 0
+        ~message:"cache should be empty after garbage collector run" )
 
-    [%test_eq: int] (Cache.count cache) 0
-      ~message:"cache should be empty after garbage collector run"
-
-  let remove_data_on_gc () =
+  let remove_data_on_gc ?(gc_strict = true) () =
     Async.Thread_safe.block_on_async_exn
     @@ fun () ->
     File_system.with_temp_dir "disk_cache-remove_data_on_gc"
-      ~f:remove_data_on_gc_impl
+      ~f:(remove_data_on_gc_impl ~gc_strict)
 
   let initialize_and_expect_failure path ~logger =
     let%bind cache_res = Cache.initialize path ~logger in
```
