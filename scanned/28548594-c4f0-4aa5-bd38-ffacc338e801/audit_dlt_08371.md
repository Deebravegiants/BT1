# [?] [backup-cli] removing dirs crate due to RUSTSEC-2020-0053

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2020-10-20
Source: https://github.com/move-language/move/commit/95954cabc9a33086d8efd35b437de4b82ec10be1
Type: security-commit

## Details
[backup-cli] removing dirs crate due to RUSTSEC-2020-0053

Closes: #6553

## Patch
### Cargo.lock
```diff
@@ -242,7 +242,6 @@ dependencies = [
  "backup-service",
  "byteorder",
  "bytes",
- "dirs 3.0.1",
  "executor",
  "executor-test-helpers",
  "executor-types",
```

### storage/backup/backup-cli/Cargo.toml
```diff
@@ -13,7 +13,6 @@ anyhow = "1.0.33"
 async-trait = "0.1.41"
 byteorder = "1.3.4"
 bytes = "0.5.6"
-dirs = "3.0.1"
 futures = "0.3.6"
 hex = "0.4.2"
 itertools = "0.9.0"
```

### storage/backup/backup-cli/src/metadata/cache.rs
```diff
@@ -38,9 +38,10 @@ impl MetadataCacheOpt {
         self.dir
             .clone()
             .unwrap_or_else(|| {
-                dirs::home_dir()
+                let home_path: PathBuf = std::env::var_os("HOME")
                     .expect("Can't find home dir. Specify metadata cache path explicitly.")
-                    .join("libra_backup_metadata")
+                    .into();
+                home_path.join("libra_backup_metadata")
             })
             .join(Self::SUB_DIR)
     }
```
