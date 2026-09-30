# [?] FIX: Don't try to call into LMDB when invoking GC, so to avoid deadlock

## Summary
Severity: Unknown
Chain: Mina
Component: MinaProtocol/mina
Published: 2025-06-30
Source: https://github.com/MinaProtocol/mina/commit/783f2d58aeb8df61042126b0780989c92d042f28
Type: security-commit

## Details
FIX: Don't try to call into LMDB when invoking GC, so to avoid deadlock

## Patch
### src/lib/disk_cache/lmdb/disk_cache.ml
```diff
@@ -16,13 +16,28 @@ module Make (Data : Binable.S) = struct
 
   module Rw = Read_write (F)
 
-  type t = { env : Rw.t; db : Rw.holder; counter : int ref; logger : Logger.t }
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
-        { env; db; counter = ref 0; logger } )
+        { env
+        ; db
+        ; counter = ref 0
+        ; logger
+        ; garbage = Hash_set.create (module Int)
+        } )
 
   type id = { idx : int }
 
@@ -31,15 +46,18 @@ module Make (Data : Binable.S) = struct
       ~metadata:[ ("index", `Int idx) ] ;
     Rw.get ~env db idx |> Option.value_exn
 
-  let put ({ env; db; counter; logger } : t) (x : Data.t) : id =
+  let put ({ env; db; counter; logger; garbage } : t) (x : Data.t) : id =
     let idx = !counter in
     incr counter ;
     let res = { idx } in
     (* When this reference is GC'd, delete the file. *)
     Gc.Expert.add_finalizer_last_exn res (fun () ->
         [%log debug] "Data at %d is GCed, removing from LMDB cache" idx
           ~metadata:[ ("index", `Int idx) ] ;
-        Rw.remove ~env db idx ) ;
+        Hash_set.add garbage idx ) ;
+    if Hash_set.length garbage >= garbage_size_limit then (
+      Hash_set.iter garbage ~f:(fun to_remove -> Rw.remove ~env db to_remove) ;
+      Hash_set.clear garbage ) ;
     Rw.set ~env db idx x ;
     res
 
```
