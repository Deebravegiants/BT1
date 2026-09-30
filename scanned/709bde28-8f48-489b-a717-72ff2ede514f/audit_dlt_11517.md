# [?] fix: upgrade iavl to v1.2.8 to fix data race in nodeDB.storageVersion (#7003)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-04-08
Source: https://github.com/celestiaorg/celestia-app/commit/84d4e794d006cabc73a8bab8d72fa73a7184e3da
Type: security-commit

## Details
fix: upgrade iavl to v1.2.8 to fix data race in nodeDB.storageVersion (#7003)

## Summary

- Upgrade `github.com/cosmos/iavl` from v1.2.6 to v1.2.8 to fix a DATA
RACE detected in `test-race` CI between
`nodeDB.SetFastStorageVersionToBatch()` (write during commit) and
`nodeDB.getStorageVersion()` (read during gRPC queries)
- The key fix is in v1.2.7
([cosmos/iavl#1144](https://github.com/cosmos/iavl/pull/1144)) which
adds `RLock`/`RUnlock` around `getStorageVersion()` and converts the
`nodeDB` mutex to `sync.RWMutex`

Closes https://github.com/celestiaorg/celestia-app/issues/7001

## Test plan

- [ ] CI `test-race` passes without DATA RACE warnings in
`TestBroadcastTx_NonSequenceGasEstimationError`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
<!-- devin-review-badge-begin -->

---

<a href="https://app.devin.ai/review/celestiaorg/celestia-app/pull/7003"
target="_blank">
  <picture>
<source media="(prefers-color-scheme: dark)"
srcset="https://static.devin.ai/assets/gh-open-in-devin-review-dark.svg?v=1">
<img
src="https://static.devin.ai/assets/gh-open-in-devin-review-light.svg?v=1"
alt="Open with Devin">
  </picture>
</a>
<!-- devin-review-badge-end -->

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### go.mod
```diff
@@ -191,7 +191,7 @@ require (
 	github.com/cockroachdb/swiss v0.0.0-20251224182025-b0f6560f979b // indirect
 	github.com/cockroachdb/tokenbucket v0.0.0-20250429170803-42689b6311bb // indirect
 	github.com/cosmos/gogogateway v1.2.0 // indirect
-	github.com/cosmos/iavl v1.2.6 // indirect
+	github.com/cosmos/iavl v1.2.8 // indirect
 	github.com/cosmos/ics23/go v0.11.0 // indirect
 	github.com/cosmos/ledger-cosmos-go v0.15.0 // indirect
 	github.com/creachadair/atomicfile v0.3.1 // indirect
```

### go.sum
```diff
@@ -1000,8 +1000,8 @@ github.com/cosmos/gogogateway v1.2.0/go.mod h1:iQpLkGWxYcnCdz5iAdLcRBSw3h7NXeOkZ
 github.com/cosmos/gogoproto v1.4.2/go.mod h1:cLxOsn1ljAHSV527CHOtaIP91kK6cCrZETRBrkzItWU=
 github.com/cosmos/gogoproto v1.7.2 h1:5G25McIraOC0mRFv9TVO139Uh3OklV2hczr13KKVHCA=
 github.com/cosmos/gogoproto v1.7.2/go.mod h1:8S7w53P1Y1cHwND64o0BnArT6RmdgIvsBuco6uTllsk=
-github.com/cosmos/iavl v1.2.6 h1:Hs3LndJbkIB+rEvToKJFXZvKo6Vy0Ex1SJ54hhtioIs=
-github.com/cosmos/iavl v1.2.6/go.mod h1:GiM43q0pB+uG53mLxLDzimxM9l/5N9UuSY3/D0huuVw=
+github.com/cosmos/iavl v1.2.8 h1:55F96BGUJ7KT7h+Ky/cEqS+pEvhFqsU4O8Th3F0N1js=
+github.com/cosmos/iavl v1.2.8/go.mod h1:FRHN4tO+6crf0p2zsqye+nAbsMgiwdkxpWm18DyP6+Y=
 github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v8 v8.2.0 h1:rM+S14DFiqmu6Rc3PuhvWqwywPsnt/CbIslSnBftPFs=
 github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v8 v8.2.0/go.mod h1:O5H9Ic3Pe6cmJn1eqlj5N48sLb8WQ1VWmDP4/11g/4E=
 github.com/cosmos/ibc-go/modules/capability v1.0.1 h1:ibwhrpJ3SftEEZRxCRkH0fQZ9svjthrX2+oXdZvzgGI=
```

### test/docker-e2e/go.mod
```diff
@@ -110,7 +110,7 @@ require (
 	github.com/cosmos/cosmos-proto v1.0.0-beta.5 // indirect
 	github.com/cosmos/go-bip39 v1.0.0 // indirect
 	github.com/cosmos/gogogateway v1.2.0 // indirect
-	github.com/cosmos/iavl v1.2.6 // indirect
+	github.com/cosmos/iavl v1.2.8 // indirect
 	github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v8 v8.2.0 // indirect
 	github.com/cosmos/ibc-go/modules/capability v1.0.1 // indirect
 	github.com/cosmos/ics23/go v0.11.0 // indirect
```

### test/docker-e2e/go.sum
```diff
@@ -906,8 +906,8 @@ github.com/cosmos/gogogateway v1.2.0/go.mod h1:iQpLkGWxYcnCdz5iAdLcRBSw3h7NXeOkZ
 github.com/cosmos/gogoproto v1.4.2/go.mod h1:cLxOsn1ljAHSV527CHOtaIP91kK6cCrZETRBrkzItWU=
 github.com/cosmos/gogoproto v1.7.2 h1:5G25McIraOC0mRFv9TVO139Uh3OklV2hczr13KKVHCA=
 github.com/cosmos/gogoproto v1.7.2/go.mod h1:8S7w53P1Y1cHwND64o0BnArT6RmdgIvsBuco6uTllsk=
-github.com/cosmos/iavl v1.2.6 h1:Hs3LndJbkIB+rEvToKJFXZvKo6Vy0Ex1SJ54hhtioIs=
-github.com/cosmos/iavl v1.2.6/go.mod h1:GiM43q0pB+uG53mLxLDzimxM9l/5N9UuSY3/D0huuVw=
+github.com/cosmos/iavl v1.2.8 h1:55F96BGUJ7KT7h+Ky/cEqS+pEvhFqsU4O8Th3F0N1js=
+github.com/cosmos/iavl v1.2.8/go.mod h1:FRHN4tO+6crf0p2zsqye+nAbsMgiwdkxpWm18DyP6+Y=
 github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v8 v8.2.0 h1:rM+S14DFiqmu6Rc3PuhvWqwywPsnt/CbIslSnBftPFs=
 github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v8 v8.2.0/go.mod h1:O5H9Ic3Pe6cmJn1eqlj5N48sLb8WQ1VWmDP4/11g/4E=
 github.com/cosmos/ibc-go/modules/capability v1.0.1 h1:ibwhrpJ3SftEEZRxCRkH0fQZ9svjthrX2+oXdZvzgGI=
```
