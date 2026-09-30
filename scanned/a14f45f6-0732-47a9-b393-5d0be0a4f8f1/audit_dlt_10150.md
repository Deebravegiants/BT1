# [?] fix: don't panic when the database is created by a higher version executable binary

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-07-27
Source: https://github.com/nervosnetwork/ckb/commit/f902055320955239158b04bb1a1c0360c4ac4fae
Type: security-commit

## Details
fix: don't panic when the database is created by a higher version executable binary

## Patch
### ckb-bin/src/subcommand/migrate.rs
```diff
@@ -1,5 +1,6 @@
 use ckb_app_config::{ExitCode, MigrateArgs};
 use ckb_launcher::migrate::Migrate;
+use std::cmp::Ordering;
 
 use crate::helper::prompt;
 
@@ -13,15 +14,25 @@ pub fn migrate(args: MigrateArgs) -> Result<(), ExitCode> {
         })?;
 
         if let Some(db) = read_only_db {
+            let db_status = migrate.check(&db);
+            if matches!(db_status, Ordering::Greater) {
+                eprintln!(
+                    "The database is created by a higher version CKB executable binary, \n\
+                     so that the current CKB executable binary couldn't open this database.\n\
+                     Please download the latest CKB executable binary."
+                );
+                return Err(ExitCode::Failure);
+            }
+
             if args.check {
-                if migrate.check(&db) {
+                if matches!(db_status, Ordering::Less) {
                     return Ok(());
                 } else {
                     return Err(ExitCode::Cli);
                 }
             }
 
-            if !migrate.check(&db) {
+            if matches!(db_status, Ordering::Equal) {
                 return Ok(());
             }
 
```

### db-migration/src/lib.rs
```diff
@@ -2,9 +2,10 @@
 use ckb_db::{ReadOnlyDB, RocksDB};
 use ckb_db_schema::{COLUMN_META, META_TIP_HEADER_KEY, MIGRATION_VERSION_KEY};
 use ckb_error::{Error, InternalErrorKind};
-use ckb_logger::{error, info};
+use ckb_logger::{debug, error, info};
 use console::Term;
 pub use indicatif::{HumanDuration, MultiProgress, ProgressBar, ProgressDrawTarget, ProgressStyle};
+use std::cmp::Ordering;
 use std::collections::BTreeMap;
 use std::sync::Arc;
 
@@ -32,10 +33,15 @@ impl Migrations {
             .insert(migration.version().to_string(), migration);
     }
 
-    /// Check whether database requires migration
+    /// Check if database's version is matched with the executable binary version.
     ///
-    /// Return true if migration is required
-    pub fn check(&self, db: &ReadOnlyDB) -> bool {
+    /// Returns
+    /// - Less: The database version is less than the matched version of the executable binary.
+    ///   Requires migration.
+    /// - Equal: The database version is matched with the executable binary version.
+    /// - Greater: The database version is greater than the matched version of the executable binary.
+    ///   Requires upgrade the executable binary.
+    pub fn check(&self, db: &ReadOnlyDB) -> Ordering {
         let db_version = match db
             .get_pinned_default(MIGRATION_VERSION_KEY)
             .expect("get the version of database")
@@ -46,15 +52,24 @@ impl Migrations {
             None => {
                 // if version is none, but db is not empty
                 // patch 220464f
-                return self.is_non_empty_rdb(db);
+                if self.is_non_empty_rdb(db) {
+                    return Ordering::Less;
+                } else {
+                    return Ordering::Equal;
+                }
             }
         };
+        debug!("current database version [{}]", db_version);
 
-        self.migrations
+        let latest_version = self
+            .migrations
             .values()
             .last()
-            .map(|m| m.version() > db_version.as_str())
-            .unwrap_or(false)
+            .unwrap_or_else(|| panic!("should have at least one version"))
+            .version();
+        debug!("latest  database version [{}]", latest_version);
+
+        db_version.as_str().cmp(latest_version)
     }
 
     /// Check if the migrations will consume a lot of time.
```

### util/launcher/src/migrate.rs
```diff
@@ -5,6 +5,7 @@ use ckb_db::{ReadOnlyDB, RocksDB};
 use ckb_db_migration::{DefaultMigration, Migrations};
 use ckb_db_schema::{COLUMNS, COLUMN_META};
 use ckb_error::Error;
+use std::cmp::Ordering;
 use std::path::PathBuf;
 
 const INIT_DB_VERSION: &str = "20191127135521";
@@ -37,8 +38,15 @@ impl Migrate {
         ReadOnlyDB::open_cf(&self.path, vec![COLUMN_META])
     }
 
-    /// Return true if migration is required
-    pub fn check(&self, db: &ReadOnlyDB) -> bool {
+    /// Check if database's version is matched with the executable binary version.
+    ///
+    /// Returns
+    /// - Less: The database version is less than the matched version of the executable binary.
+    ///   Requires migration.
+    /// - Equal: The database version is matched with the executable binary version.
+    /// - Greater: The database version is greater than the matched version of the executable binary.
+    ///   Requires upgrade the executable binary.
+    pub fn check(&self, db: &ReadOnlyDB) -> Ordering {
         self.migrations.check(&db)
     }
 
```

### util/launcher/src/shared_builder.rs
```diff
@@ -27,6 +27,7 @@ use ckb_types::core::HeaderView;
 use ckb_types::packed::Byte32;
 use ckb_verification::cache::TxVerifyCache;
 use p2p::SessionId as PeerIndex;
+use std::cmp::Ordering;
 use std::collections::HashSet;
 use std::path::PathBuf;
 use std::sync::atomic::AtomicBool;
@@ -49,40 +50,45 @@ pub struct SharedBuilder {
 pub fn open_or_create_db(config: &DBConfig) -> Result<RocksDB, ExitCode> {
     let migrate = Migrate::new(&config.path);
 
-    let mut db_exist = false;
+    let read_only_db = migrate.open_read_only_db().map_err(|e| {
+        eprintln!("migrate error {}", e);
+        ExitCode::Failure
+    })?;
 
-    // migration prompt
-    {
-        let read_only_db = migrate.open_read_only_db().map_err(|e| {
-            eprintln!("migrate error {}", e);
-            ExitCode::Failure
-        })?;
-
-        if let Some(db) = read_only_db {
-            db_exist = true;
-
-            if migrate.require_expensive(&db) {
+    if let Some(db) = read_only_db {
+        match migrate.check(&db) {
+            Ordering::Greater => {
                 eprintln!(
-                    "For optimal performance, CKB wants to migrate the data into new format.\n\
-                    You can use the old version CKB if you don't want to do the migration.\n\
-                    We strongly recommended you to use the latest stable version of CKB, \
-                    since the old versions may have unfixed vulnerabilities.\n\
-                    Run `ckb migrate --help` for more information about migration."
+                    "The database is created by a higher version CKB executable binary, \n\
+                     so that the current CKB executable binary couldn't open this database.\n\
+                     Please download the latest CKB executable binary."
                 );
-                return Err(ExitCode::Failure);
+                Err(ExitCode::Failure)
+            }
+            Ordering::Equal => Ok(RocksDB::open(config, COLUMNS)),
+            Ordering::Less => {
+                if migrate.require_expensive(&db) {
+                    eprintln!(
+                        "For optimal performance, CKB wants to migrate the data into new format.\n\
+                        You can use the old version CKB if you don't want to do the migration.\n\
+                        We strongly recommended you to use the latest stable version of CKB, \
+                        since the old versions may have unfixed vulnerabilities.\n\
+                        Run `ckb migrate --help` for more information about migration."
+                    );
+                    Err(ExitCode::Failure)
+                } else {
+                    Ok(RocksDB::open(config, COLUMNS))
+                }
             }
         }
-    }
-
-    let db = RocksDB::open(config, COLUMNS);
-    if !db_exist {
+    } else {
+        let db = RocksDB::open(config, COLUMNS);
         migrate.init_db_version(&db).map_err(|e| {
             eprintln!("migrate init_db_version error {}", e);
             ExitCode::Failure
         })?;
+        Ok(db)
     }
-
-    Ok(db)
 }
 
 impl SharedBuilder {
```
