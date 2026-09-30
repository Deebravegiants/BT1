# [?] build(store): repin cronos-store to fix historical-query use-after-free and merge-iterator overhead (#2181)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/cronos
Published: 2026-08-07
Source: https://github.com/crypto-org-chain/cronos/commit/7aa5afe37285c07e52f27ed92b794e656875744e
Type: security-commit

## Details
build(store): repin cronos-store to fix historical-query use-after-free and merge-iterator overhead (#2181)

* build: repin cronos-store to crypto-org-chain/cronos-store#110

Picks up the historical-query zero-copy use-after-free fix and the
merge-iterator copy-overhead fix.

* docs: add changelog entry for cronos-store repin

* build: bump cronos-store pin to PR#110 branch head

Picks up the golangci-lint import-grouping/spelling fixup commit.

* docs: cover merge-iterator perf fix in changelog entry

* fix(store): tidy go.sum for cosmos-sdk repin, trim changelog entry

go.sum was missing entries for the newer cosmos-sdk pseudo-version,
failing golangci-lint and unittest CI. Also merge the duplicate Chores
header and trim the #2181 changelog line per review feedback.

---------

Signed-off-by: JayT106 <JayT106@users.noreply.github.com>

## Patch
### AGENT.md
```diff
@@ -137,7 +137,7 @@ upstream project on GitHub — the fork can and does differ. Resolve the actual
 | Cosmos SDK (app framework, auth/bank/gov/staking, ante handlers, baseapp) | `github.com/cosmos/cosmos-sdk` | **`github.com/crypto-org-chain/cosmos-sdk`** (fork) | `v0.54.4-...20260805154329-743fc8dc9dbc` |
 | EVM execution & JSON-RPC (`x/evm`, `x/feemarket`, statedb) | `github.com/evmos/ethermint` | **`github.com/crypto-org-chain/ethermint`** (fork) | `v0.22.1-...20260702171011-a639532d9759` |
 | Consensus / networking / mempool | `github.com/cometbft/cometbft` | **`github.com/crypto-org-chain/cometbft`** (fork) | `v0.0.0-...20260729145603-14b7b93046e3` |
-| Custom store: memiavl, versiondb, store | `github.com/crypto-org-chain/cronos-store/{memiavl,versiondb,store}` | **`crypto-org-chain/cronos-store`** (fork target pins) | `...20260728044748-2fd6432e07e1` |
+| Custom store: memiavl, versiondb, store | `github.com/crypto-org-chain/cronos-store/{memiavl,versiondb,store}` | **`crypto-org-chain/cronos-store`** (fork target pins) | `...20260806235227-c224b839a4b1` |
 | EVM crypto / core types | `github.com/ethereum/go-ethereum` | **`github.com/crypto-org-chain/go-ethereum`** (fork) | `v1.10.20-...20260521015249` |
 | IBC | `github.com/cosmos/ibc-go/v11` | upstream | `v11.1.0` |
 
```

### CHANGELOG.md
```diff
@@ -23,6 +23,7 @@
 
 * [#2180](https://github.com/crypto-org-chain/cronos/pull/2180) chore: bump golang.org/x/text to v0.39.0.
 * [#2157](https://github.com/crypto-org-chain/cronos/pull/2157) chore: repin cronos-store, cometbft v0.39, cosmos-sdk v0.54 forks.
+* [#2181](https://github.com/crypto-org-chain/cronos/pull/2181) build(store): repin cronos-store to fix historical-query use-after-free and merge-iterator overhead.
 
 
 *Jul 16, 2026*
```

### go.mod
```diff
@@ -391,9 +391,9 @@ replace (
 	// release/v0.54.x
 	github.com/cosmos/cosmos-sdk => github.com/crypto-org-chain/cosmos-sdk v0.54.4-0.20260805154329-743fc8dc9dbc
 	// master
-	github.com/crypto-org-chain/cronos-store/memiavl => github.com/crypto-org-chain/cronos-store/memiavl v0.0.0-20260728044748-2fd6432e07e1
-	github.com/crypto-org-chain/cronos-store/store => github.com/crypto-org-chain/cronos-store/store v0.0.0-20260728044748-2fd6432e07e1
-	github.com/crypto-org-chain/cronos-store/versiondb => github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260728044748-2fd6432e07e1
+	github.com/crypto-org-chain/cronos-store/memiavl => github.com/crypto-org-chain/cronos-store/memiavl v0.0.0-20260806235227-c224b839a4b1
+	github.com/crypto-org-chain/cronos-store/store => github.com/crypto-org-chain/cronos-store/store v0.0.0-20260806235227-c224b839a4b1
+	github.com/crypto-org-chain/cronos-store/versiondb => github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260806235227-c224b839a4b1
 	// release/v1.16
 	github.com/ethereum/go-ethereum => github.com/crypto-org-chain/go-ethereum v1.10.20-0.20260521015249-663dca6c618e
 
```

### go.sum
```diff
@@ -292,12 +292,12 @@ github.com/crypto-org-chain/cometbft v0.0.0-20260729145603-14b7b93046e3 h1:kw6+G
 github.com/crypto-org-chain/cometbft v0.0.0-20260729145603-14b7b93046e3/go.mod h1:KcZvZTqdLgOisktAoWwwcS2fgO4E110r44KxEGyq8SI=
 github.com/crypto-org-chain/cosmos-sdk v0.54.4-0.20260805154329-743fc8dc9dbc h1:1bj7uwX9gxoxqmWSOQs6+Iz2jse95DRu6w1OQNfiiis=
 github.com/crypto-org-chain/cosmos-sdk v0.54.4-0.20260805154329-743fc8dc9dbc/go.mod h1:d+mzrQ+PV+6t63HomWzLx+OoFeprkjO/b+0ih+LfvIo=
-github.com/crypto-org-chain/cronos-store/memiavl v0.0.0-20260728044748-2fd6432e07e1 h1:t+dIfkWJzSLqUQkYNplKRFPbhkujP555reKG+fOHsQo=
-github.com/crypto-org-chain/cronos-store/memiavl v0.0.0-20260728044748-2fd6432e07e1/go.mod h1:pDMnEFkR+qMEeiTUA07p0Xk4qM1qaCHrHqbR96kJGbQ=
-github.com/crypto-org-chain/cronos-store/store v0.0.0-20260728044748-2fd6432e07e1 h1:QVtIMSqjDP3TfU9EtXA3Ylq6P/+an+3EFtjdkD1yW9Y=
-github.com/crypto-org-chain/cronos-store/store v0.0.0-20260728044748-2fd6432e07e1/go.mod h1:nbT4YcTZJqW0EY1zNO/o7hx+a0q2hCEjsnZi5vQy2N4=
-github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260728044748-2fd6432e07e1 h1:1ypu5xtFyKwpwxxs0ADh4ecDaWixuutLUnxyp1zHT7I=
-github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260728044748-2fd6432e07e1/go.mod h1:vNigSKdbXLtFT5wQMaOyLMMXJn3DxL8GRG8cnOZbfUc=
+github.com/crypto-org-chain/cronos-store/memiavl v0.0.0-20260806235227-c224b839a4b1 h1:r1349nKosU4EEMdXcXO8ALe9CQaViS4uU3p8l8w3h30=
+github.com/crypto-org-chain/cronos-store/memiavl v0.0.0-20260806235227-c224b839a4b1/go.mod h1:pDMnEFkR+qMEeiTUA07p0Xk4qM1qaCHrHqbR96kJGbQ=
+github.com/crypto-org-chain/cronos-store/store v0.0.0-20260806235227-c224b839a4b1 h1:RYDGSK9kxGpj/KeA+gfLPEd96x/0/FLHnIrKzzJ0MH4=
+github.com/crypto-org-chain/cronos-store/store v0.0.0-20260806235227-c224b839a4b1/go.mod h1:nbT4YcTZJqW0EY1zNO/o7hx+a0q2hCEjsnZi5vQy2N4=
+github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260806235227-c224b839a4b1 h1:mu6eq9byuLHr18iF4T8y4OnejRC06OJiZi58cww//2U=
+github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260806235227-c224b839a4b1/go.mod h1:vNigSKdbXLtFT5wQMaOyLMMXJn3DxL8GRG8cnOZbfUc=
 github.com/crypto-org-chain/ethermint v0.22.1-0.20260727155757-43e83c52f91d h1:O2KeqS1MP7aDbIrcvjpC51Kwq+pOp4DBvT+piWx+aW4=
 github.com/crypto-org-chain/ethermint v0.22.1-0.20260727155757-43e83c52f91d/go.mod h1:lld1JVNvUH0RZn4n3mSl3qhTJCXeaZsuhTcz3ZQ5kak=
 github.com/crypto-org-chain/go-ethereum v1.10.20-0.20260521015249-663dca6c618e h1:ftyRRWDiXKWsnp3PxLNbfVLzrqkx+aDNZdkPconawWk=
```

### gomod2nix.toml
```diff
@@ -302,15 +302,15 @@ schema = 3
     version = "v0.0.29"
     hash = "sha256-QP39Y1YMGWQSIAaD92s6LVLERgwh+5004a7U3flUTU8="
   [mod."github.com/crypto-org-chain/cronos-store/memiavl"]
-    version = "v0.0.0-20260728044748-2fd6432e07e1"
-    hash = "sha256-LtB0bztRrf/haoWRVJstPD+efVeYQ0y1LyUB31Mx07Y="
+    version = "v0.0.0-20260806235227-c224b839a4b1"
+    hash = "sha256-7AdHQjSa6M6gESfKdXAwJLM+ALgtxWqLkKYIlsjX2Tk="
     replaced = "github.com/crypto-org-chain/cronos-store/memiavl"
   [mod."github.com/crypto-org-chain/cronos-store/store"]
-    version = "v0.0.0-20260728044748-2fd6432e07e1"
-    hash = "sha256-aj1XWMzg7x5pwKwf/mTFRVghZRSHO+1tJrty7uDihNU="
+    version = "v0.0.0-20260806235227-c224b839a4b1"
+    hash = "sha256-N0TYukNwMH66J+i530opwuzBJWzfLrixgM1pChgKK0w="
     replaced = "github.com/crypto-org-chain/cronos-store/store"
   [mod."github.com/crypto-org-chain/cronos-store/versiondb"]
-    version = "v0.0.0-20260728044748-2fd6432e07e1"
+    version = "v0.0.0-20260806235227-c224b839a4b1"
     hash = "sha256-SIIJ6Is7MccaSzlGA4Gz6xo1DWHWYRoEG9lkFsgqDxs="
     replaced = "github.com/crypto-org-chain/cronos-store/versiondb"
   [mod."github.com/danieljoos/wincred"]
```
