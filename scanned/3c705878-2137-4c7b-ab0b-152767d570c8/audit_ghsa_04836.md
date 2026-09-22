# [M] Klever-Go KVM: Throttler slot leak in trie account-data sync causes epoch bootstrap / state sync DoS

## Summary
Severity: Medium
Advisory: GHSA-fw38-pc54-jvx9
CVE: CVE-2026-49343
CWE: CWE-400, CWE-772
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-fw38-pc54-jvx9
Type: github-advisory

## Affected
- Go: `github.com/klever-io/klever-go` — affected >=0 <1.7.18

## Details
## Summary

  The account-data trie syncers leak bounded throttler slots on error paths in `syncDataTrie()`. Each failed trie sync permanently consumes one slot from
  the `NumGoRoutinesThrottler`, and the slot is never returned unless the sync succeeds or the root hash was already present.

  I confirmed this on the current default branch `develop` at commit `9640d63` (observed on May 20, 2026). I also confirmed the bug with a runtime PoC
  using the real timeout path in `trieSyncer.StartSyncing()`: two timed-out sync attempts are enough to exhaust a throttler with capacity `2`.

  This affects the epoch bootstrap path because `syncUserAccountsState()` and `syncKappAccountsState()` create bounded throttlers and abort bootstrap
  immediately if the syncer returns an error. Once enough trie-root sync attempts fail, the syncer cannot make forward progress and bootstrap fails.

  ## Affected Components

  - `data/syncer/userAccountsSyncer.go`
  - `data/syncer/kappAccountsSyncer.go`
  - `data/trie/sync.go`
  - `core/throttler/numGoRoutinesThrottler.go`
  - `core/bootstrap/process.go`

  ## Affected Version

  Verified on:
  - `develop` HEAD `9640d63`

  Please check whether the same code is present in supported `1.7.x` releases.

  ## Suggested Severity

  High

  ## Vulnerability Details

  ### Root Cause

  Both account-data syncers call `StartProcessing()` before creating / starting the trie syncer, but they only call `EndProcessing()` on the success path
  and on the duplicate-root early return.

  `userAccountsSyncer.syncDataTrie()`:

  ```go
  func (u *userAccountsSyncer) syncDataTrie(rootHash []byte, ssh data.SyncStatisticsHandler, ctx context.Context) error {
      u.throttler.StartProcessing()

      u.syncerMutex.Lock()
      if _, ok := u.dataTries[string(rootHash)]; ok {
          u.syncerMutex.Unlock()
          u.throttler.EndProcessing()
          return nil
      }

      dataTrie, err := trie.NewTrie(...)
      if err != nil {
          u.syncerMutex.Unlock()
          return err
      }

      trieSyncer, err := trie.NewTrieSyncer(arg)
      if err != nil {
          u.syncerMutex.Unlock()
          return err
      }

      u.syncerMutex.Unlock()

      err = trieSyncer.StartSyncing(rootHash, ctx)
      if err != nil {
          return err
      }

      u.throttler.EndProcessing()
      return nil
  }

  The same bug exists in kappAccountsSyncer.syncDataTrie().
```
  ### Missing slot release paths

  After StartProcessing(), the following error paths return without EndProcessing():

  1. trie.NewTrie(...) returns an error
  2. trie.NewTrieSyncer(...) returns an error
  3. trieSyncer.StartSyncing(...) returns an error

  ### Why this matters

  NumGoRoutinesThrottler is a strict bounded counter:
```
  func (ngrt *NumGoRoutinesThrottler) CanProcess() bool {
      valCounter := atomic.LoadInt32(&ngrt.counter)
      return valCounter < ngrt.max
  }

  func (ngrt *NumGoRoutinesThrottler) StartProcessing() {
      atomic.AddInt32(&ngrt.counter, 1)
  }

  func (ngrt *NumGoRoutinesThrottler) EndProcessing() {
      atomic.AddInt32(&ngrt.counter, -1)
  }

  Once leaked, a slot remains consumed for the lifetime of that throttler instance.

  The parent loops in both syncers wait for capacity before starting the next account-data trie sync:

  for !u.throttler.CanProcess() {
      select {
      case <-time.After(timeBetweenRetries):
          continue
      case <-ctx.Done():
          return common.ErrTimeIsOut
      }
  }
```
  So after enough failures, further roots stop progressing and the sync operation eventually returns time is out.

  ### Bootstrap impact

  Epoch bootstrap uses these syncers directly and aborts on any error:
```
  err = e.syncUserAccountsState(e.epochStartMeta.Header.TrieRoot)
  if err != nil {
      return nil, nil, err
  }

  err = e.syncKappAccountsState(e.epochStartMeta.Header.KAppsTrieRoot)
  if err != nil {
      return nil, nil, err
  }
```
  The throttlers for these paths are real bounded throttlers created from numConcurrentTrieSyncers.

  ## Proof of Concept

  I verified the bug with the real timeout path, not only with a canceled context.

  The PoC below uses:

  - a real NumGoRoutinesThrottler with capacity 2
  - a real trieSyncer.StartSyncing()
  - an empty trie-node cache and a request handler that never supplies nodes
  - a short sync timeout (1s) so StartSyncing() returns trie.ErrTimeIsOut

  After the first failed sync, one slot remains leaked.
  After the second failed sync, the throttler is exhausted.

  ### PoC test
```
  package syncer

  import (
        "context"
        "testing"
        "time"

        commonmock "github.com/klever-io/klever-go/common/mock"
        corethrottler "github.com/klever-io/klever-go/core/throttler"
        "github.com/klever-io/klever-go/data"
        "github.com/klever-io/klever-go/data/trie"
        triestats "github.com/klever-io/klever-go/data/trie/statistics"
        "github.com/stretchr/testify/require"
  )

  func newBaseSyncerForTimeoutPOC(t *testing.T) *baseAccountsSyncer {
        t.Helper()

        storageManager, err := trie.NewTrieStorageManagerWithoutPruning(commonmock.NewMemDbMock())
        require.NoError(t, err)

        return &baseAccountsSyncer{
                hasher:                    commonmock.HasherMock{},
                marshalizer:               &commonmock.MarshalizerMock{},
                trieSyncers:               make(map[string]data.TrieSyncer),
                dataTries:                 make(map[string]data.Trie),
                trieStorageManager:        storageManager,
                requestHandler:            &commonmock.RequestHandlerStub{},
                timeout:                   time.Second,
                cacher:                    commonmock.NewCacherStub(),
                maxTrieLevelInMemory:      5,
                name:                      "timeout-poc",
                maxHardCapForMissingNodes: 1,
        }
  }

  func TestPOC_UserAccountsSyncer_LeaksThrottlerSlotOnTrieTimeout(t *testing.T) {
        thr, err := corethrottler.NewNumGoRoutinesThrottler(2)
        require.NoError(t, err)

        s := &userAccountsSyncer{
                baseAccountsSyncer: newBaseSyncerForTimeoutPOC(t),
                throttler:          thr,
        }

        err = s.syncDataTrie([]byte("missing-root-1"), triestats.NewTrieSyncStatistics(), context.Background())
        require.ErrorIs(t, err, trie.ErrTimeIsOut)
        require.True(t, thr.CanProcess())

        err = s.syncDataTrie([]byte("missing-root-2"), triestats.NewTrieSyncStatistics(), context.Background())
        require.ErrorIs(t, err, trie.ErrTimeIsOut)
        require.False(t, thr.CanProcess())
  }

  func TestPOC_KappAccountsSyncer_LeaksThrottlerSlotOnTrieTimeout(t *testing.T) {
        thr, err := corethrottler.NewNumGoRoutinesThrottler(2)
        require.NoError(t, err)

        s := &kappAccountsSyncer{
                baseAccountsSyncer: newBaseSyncerForTimeoutPOC(t),
                throttler:          thr,
        }

        err = s.syncDataTrie([]byte("missing-root-1"), triestats.NewTrieSyncStatistics(), context.Background())
        require.ErrorIs(t, err, trie.ErrTimeIsOut)
        require.True(t, thr.CanProcess())

        err = s.syncDataTrie([]byte("missing-root-2"), triestats.NewTrieSyncStatistics(), context.Background())
        require.ErrorIs(t, err, trie.ErrTimeIsOut)
        require.False(t, thr.CanProcess())
  }
```
  ### Command used
```
  go test ./data/syncer -run 'TestPOC_(User|Kapp)AccountsSyncer_LeaksThrottlerSlotOnTrieTimeout' -count=1
```
  ### Result
```
  ok    github.com/klever-io/klever-go/data/syncer      4.005s
```
  This confirms the leak with the real timeout path from trieSyncer.StartSyncing().

  ## Impact

  An attacker who can repeatedly cause trie-node sync failures or timeouts during bootstrap can consume the bounded sync throttler until no capacity
  remains.

  Once enough slots are leaked:

  - additional account-data trie sync attempts stop making progress
  - the parent loop waits until context timeout
  - SyncAccounts() fails
  - epoch bootstrap fails

  This is a core node availability issue. It affects fresh/restarting nodes and validators that need to bootstrap or resync state.

  This is not a theoretical issue:

  - StartSyncing() performs network-dependent trie-node retrieval
  - it already has explicit timeout / failure paths
  - the leaked throttler slots are confirmed by runtime PoC

  ## Recommended Fix

  Release the slot with defer immediately after StartProcessing() and cancel the defer only if ownership is intentionally transferred, which is not the
  case here.

  Example fix pattern:
```
  func (u *userAccountsSyncer) syncDataTrie(rootHash []byte, ssh data.SyncStatisticsHandler, ctx context.Context) error {
      u.throttler.StartProcessing()
      defer u.throttler.EndProcessing()

      u.syncerMutex.Lock()
      defer u.syncerMutex.Unlock()

      if _, ok := u.dataTries[string(rootHash)]; ok {
          return nil
      }

      dataTrie, err := trie.NewTrie(...)
      if err != nil {
          return err
      }

      trieSyncer, err := trie.NewTrieSyncer(arg)
      if err != nil {
          return err
      }

      u.trieSyncers[string(rootHash)] = trieSyncer
      return trieSyncer.StartSyncing(rootHash, ctx)
  }
```
  The same pattern should be applied to:

  - data/syncer/userAccountsSyncer.go
  - data/syncer/kappAccountsSyncer.go

  ## References

  - data/syncer/userAccountsSyncer.go
  - data/syncer/kappAccountsSyncer.go
  - data/trie/sync.go
  - core/throttler/numGoRoutinesThrottler.go
  - core/bootstrap/process.go
  - SECURITY.md

## References
- https://github.com/klever-io/klever-go/security/advisories/GHSA-fw38-pc54-jvx9
- https://github.com/klever-io/klever-go
- https://github.com/klever-io/klever-go/releases/tag/v1.7.18
