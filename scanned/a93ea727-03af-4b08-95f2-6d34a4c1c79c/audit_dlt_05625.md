# [?] db/state: fix FilesAmount data race with background file integration (#22264)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-06
Source: https://github.com/erigontech/erigon/commit/bb96f7be9e5ceda83878411d4ffa145df2b25a64
Type: security-commit

## Details
db/state: fix FilesAmount data race with background file integration (#22264)

## What

`Aggregator.FilesAmount()` read each domain's / inverted index's
`dirtyFiles.Len()` without taking `dirtyFilesLock`. In `tidwall/btree`,
`Len()` does not take the tree's internal mutex (it's a plain read of
`tr.count`) even when the tree is created with internal locking, so
callers must synchronize externally. This races concurrent
`dirtyFiles.Set` from background file integration
(`integrateDirtyFiles`), which mutates the tree.

The race tripped the race-tests job on `main`
([run](https://github.com/erigontech/erigon/actions/runs/28785362605/job/85350623665)):
`TestEngineApiUnwindAcrossDomainStepBoundaries` failed with `race
detected during execution of test`. Its `waitForDomainFilesSettled`
helper (added in #21973) polls `FilesAmount()` while the background
builder is integrating files — that helper is the function's only
caller, so the race became reachable when #21973 merged. The same
`test-all-erigon-race.yml` runs in the merge-queue CI Gate, so this can
flake any PR until fixed.

## Fix

Take `a.dirtyFilesLock` in `FilesAmount()`, matching every other
`dirtyFiles` reader in `aggregator.go`. The write side
(`IntegrateDirtyFiles`) already holds this lock.

## Test

TDD: the new `TestFilesAmountConcurrent` (modeled on the neighboring
`TestReferencesInCommitmentBranchesConcurrent`) deterministically
reproduces the race under `-race` — it fails on `main` with the exact
stacks from the CI failure (`FilesAmount` → `btree.Len` racing
`btree.Set`) and passes with the fix.

Related: #15342 (audit of unsynchronized `dirtyFiles` access —
`FilesAmount` wasn't in its list).
