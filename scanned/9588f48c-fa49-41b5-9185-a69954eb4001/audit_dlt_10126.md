# [?] fix(script): fixed panic when calling inherited_fds in root process

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2024-10-15
Source: https://github.com/nervosnetwork/ckb/commit/4e06387b6a25b24d65c4645f4a64004f00e81d9d
Type: security-commit

## Details
fix(script): fixed panic when calling inherited_fds in root process

## Patch
### script/src/scheduler.rs
```diff
@@ -462,7 +462,11 @@ where
                     );
                 }
                 Message::InheritedFileDescriptor(vm_id, args) => {
-                    let inherited_fd = self.inherited_fd[&vm_id].clone();
+                    let inherited_fd = if vm_id == ROOT_VM_ID {
+                        Vec::new()
+                    } else {
+                        self.inherited_fd[&vm_id].clone()
+                    };
                     let (_, machine) = self.ensure_get_instantiated(&vm_id)?;
                     let FdArgs {
                         buffer_addr,
```

### script/src/verify/tests/ckb_latest/features_since_v2023.rs
```diff
@@ -1235,6 +1235,12 @@ fn check_spawn_index_out_of_bound() {
     assert_eq!(result.is_ok(), SCRIPT_VERSION == ScriptVersion::V2);
 }
 
+#[test]
+fn check_root_inherited_fds() {
+    let result = simple_spawn_test("testdata/spawn_cases", &[19]);
+    assert_eq!(result.is_ok(), SCRIPT_VERSION == ScriptVersion::V2);
+}
+
 #[test]
 fn check_spawn_cycles() {
     let script_version = SCRIPT_VERSION;
```

### script/testdata/spawn_cases.c
```diff
@@ -536,6 +536,17 @@ int parent_index_out_of_bound(uint64_t* pid) {
     return err;
 }
 
+int parent_root_inherited_fds() {
+    uint64_t fds[2] = {0};
+    uint64_t length = 2;
+    int err = ckb_inherited_fds(fds, &length);
+    CHECK(err);
+    CHECK2(length == 0, -1);
+    err = 0;
+exit:
+    return err;
+}
+
 int parent_entry(int case_id) {
     int err = 0;
     uint64_t pid = 0;
@@ -577,6 +588,8 @@ int parent_entry(int case_id) {
         return parent_invaild_index(&pid);
     } else if (case_id == 18) {
         return parent_index_out_of_bound(&pid);
+    } else if (case_id == 19) {
+        return parent_root_inherited_fds();
     } else {
         CHECK2(false, -2);
     }
```
