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


_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/55fbb98f6a1923b88249db85ee6413e472beb843_
