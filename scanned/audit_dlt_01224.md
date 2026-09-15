# [?] [SharovBot] db/migrations: fix stage-exec-test panic on BlockAccessList table missing (#20198)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-27
Source: https://github.com/erigontech/erigon/commit/55fbb98f6a1923b88249db85ee6413e472beb843
Type: security-commit

## Details
[SharovBot] db/migrations: fix stage-exec-test panic on BlockAccessList table missing (#20198)

## Problem

The `stage-exec-test` CI job fails on commit `93b23d4` with:

```
panic: fail to open mdbx: db-table doesn't exists: BlockAccessList, label: chaindata, key not found.
Tip: try run `integration run_migrations` to create non-existing tables
github.com/erigontech/erigon/cmd/integration/commands.openDB(...)
cmd/integration/commands/root.go:102
```

CI failure:
https://github.com/erigontech/erigon/actions/runs/23649891131/job/68891618181

## Root Cause

`BlockAccessList` was added to `ChaindataTables` in `db/kv/tables.go`
but no DB migration was written to create it in **existing** databases.
The `integration` tool opens `chaindata` in **accede mode** (to coexist
with a running Erigon node without acquiring exclusive lock). In accede
mode, MDBX cannot create new tables — it panics if a table from the
schema is missing from the DB file.

Additionally, the previous flow in `openDB()` checked for pending
migrations **after** calling `opts.MustOpen()` in accede mode, meaning
the panic occurred before migrations could ever be applied.

## Fix

**1. New no-op migration `db_schema_version6`**
(`db/migrations/db_schema_version6.go`)

When this migration runs, the DB is opened in exclusive mode. The MDBX
wrapper's `openDBIs()` call in exclusive mode creates any missing tables
from `ChaindataTables` (including `BlockAccessList`) as a side-effect.

**2. Restructure `openDB()`** (`cmd/integration/commands/root.go`)

Migrations are now checked and applied **before** the accede-mode
`opts.MustOpen()` call. This ensures any new tables are created in the
exclusive-mode pass before the accede-mode open attempts to open them.

## Verification

- `go build ./cmd/integration/...` passes ✅
- `go test ./db/migrations/...` passes ✅
- No test files modified ✅

Co-authored-by: erigon-copilot[bot] <erigon-copilot[bot]@users.noreply.github.com>
Co-authored-by: Giulio Rebuffo <giulio.rebuffo@gmail.com>

### cmd/integration/commands/root.go
```diff
@@ -99,12 +99,15 @@ func openDB(opts kv2.MdbxOpts, applyMigrations bool, chain string, logger log.Lo
 		panic(opts.GetLabel())
 	}
 
-	rawDB := opts.MustOpen()
+	// Apply migrations BEFORE the accede-mode open. In accede mode MDBX cannot
+	// create new tables, so if a table was added to the schema after the DB was
+	// originally created (e.g. BlockAccessList) the open would panic. The
+	// exclusive-mode open used during migration creates any missing tables as a
+	// side-effect, preventing the subsequent accede-mode open from panicking.
 	if applyMigrations {
 		dirs := datadir.New(datadirCli)
 		migrationsDB, err := migrations.OpenMigrationsDB(dirs.Migrations, logger)
 		if err != nil {
-			rawDB.Close()
 			return nil, fmt.Errorf("open migrations db: %w", err)
 		}
 		defer migrationsDB.Close()
@@ -116,16 +119,17 @@ func openDB(opts kv2.MdbxOpts, applyMigrations bool, chain string, logger log.Lo
 		}
 		if has {
 			logger.Info("Re-Opening DB in exclusive mode to apply DB migrations")
-			rawDB.Close()
-			rawDB = opts.Exclusive(true).MustOpen()
-			if err := migrator.Apply(rawDB, migrationsDB, datadirCli, "", logger); err != nil {
+			rawDBExcl := opts.Exclusive(true).MustOpen()
+			if err := migrator.Apply(rawDBExcl, migrationsDB, datadirCli, "", logger); err != nil {
+				rawDBExcl.Close()
 				return nil, err
 			}
-			rawDB.Close()
-			rawDB = opts.MustOpen()
+			rawDBExcl.Close()
 		}
 	}
 
+	rawDB := opts.MustOpen()
+
 	dirs := datadir.New(datadirCli)
 	if err := CheckSaltFilesExist(dirs); err != nil {
 		return nil, err
```

### db/migrations/db_schema_version6.go
```diff
@@ -0,0 +1,49 @@
+// Copyright 2024 The Erigon Authors
+// This file is part of Erigon.
+//
+// Erigon is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// Erigon is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with Erigon. If not, see <http://www.gnu.org/licenses/>.
+
+package migrations
+
+import (
+	"context"
+
+	"github.com/erigontech/erigon/common/log/v3"
+	"github.com/erigontech/erigon/db/datadir"
+	"github.com/erigontech/erigon/db/kv"
+)
+
+// dbSchemaVersion6 is a no-op migration whose sole purpose is to trigger an
+// exclusive (non-accede) DB open for existing databases. When the DB is opened
+// exclusively the MDBX wrapper creates any missing tables listed in
+// ChaindataTables (e.g. BlockAccessList). Without this migration, opening an
+// existing chaindata in accede mode panics if a new table has been added to
+// the schema since the DB was created.
+var dbSchemaVersion6 = Migration{
+	Name: "db_schema_version6",
+	Up: func(db kv.RwDB, dirs datadir.Dirs, progress []byte, BeforeCommit Callback, logger log.Logger) (err error) {
+		tx, err := db.BeginRw(context.Background())
+		if err != nil {
+			return err
+		}
+		defer tx.Rollback()
+
+		// No-op: the exclusive DB open triggered by the migration mechanism
+		// is sufficient to create any new tables (e.g. BlockAccessList).
+		if err := BeforeCommit(tx, nil, true); err != nil {
+			return err
+		}
+		return tx.Commit()
+	},
+}
```

### db/migrations/migrations.go
```diff
@@ -53,6 +53,7 @@ var migrations = map[kv.Label][]Migration{
 	dbcfg.ChainDB: {
 		dbSchemaVersion5,
 		ResetStageTxnLookup,
+		dbSchemaVersion6,
 	},
 	dbcfg.TxPoolDB: {},
 	dbcfg.SentryDB: {},
```
