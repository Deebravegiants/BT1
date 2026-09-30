# [?] fix(deps): bump cronos-store to pick up memiavl WAL wait and prune underflow fixes (#2215)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/cronos
Published: 2026-09-23
Source: https://github.com/crypto-org-chain/cronos/commit/6127f66bdea08e7677fbd805d528d245e8edcccc
Type: security-commit

## Details
fix(deps): bump cronos-store to pick up memiavl WAL wait and prune underflow fixes (#2215)

* chore: bump cronos-store to 2d12c23

* chore: update changelog, gomod2nix.toml, and AGENT.md for cronos-store bump

* chore: move changelog entry to Bug fixes to match PR title

## Patch
### AGENT.md
```diff
@@ -137,7 +137,7 @@ upstream project on GitHub — the fork can and does differ. Resolve the actual
 | Cosmos SDK (app framework, auth/bank/gov/staking, ante handlers, baseapp) | `github.com/cosmos/cosmos-sdk` | **`github.com/crypto-org-chain/cosmos-sdk`** (fork) | `v0.54.4-...20260805154329-743fc8dc9dbc` |
 | EVM execution & JSON-RPC (`x/evm`, `x/feemarket`, statedb) | `github.com/evmos/ethermint` | **`github.com/crypto-org-chain/ethermint`** (fork) | `v0.22.1-...20260922081214-84a631b06a9b` |
 | Consensus / networking / mempool | `github.com/cometbft/cometbft` | **`github.com/crypto-org-chain/cometbft`** (fork) | `v0.0.0-...20260729145603-14b7b93046e3` |
-| Custom store: memiavl, versiondb, store | `github.com/crypto-org-chain/cronos-store/{memiavl,versiondb,store}` | **`crypto-org-chain/cronos-store`** (fork target pins) | `...20260807143651-cbef7554cdc3` |
+| Custom store: memiavl, versiondb, store | `github.com/crypto-org-chain/cronos-store/{memiavl,versiondb,store}` | **`crypto-org-chain/cronos-store`** (fork target pins) | `...20260923061457-2d12c238d139` |
 | EVM crypto / core types | `github.com/ethereum/go-ethereum` | **`github.com/crypto-org-chain/go-ethereum`** (fork) | `v1.10.20-...20260521015249` |
 | IBC | `github.com/cosmos/ibc-go/v11` | upstream | `v11.1.0` |
 
```

### CHANGELOG.md
```diff
@@ -13,6 +13,7 @@
 
 ### Bug fixes
 
+* [#2215](https://github.com/crypto-org-chain/cronos/pull/2215) fix(deps): bump cronos-store to pick up memiavl WAL wait and prune underflow fixes.
 * [#2214](https://github.com/crypto-org-chain/cronos/pull/2214) fix(deps): bump ethermint to reject nonempty fee granter on EIP-712 signing paths.
 * [#2179](https://github.com/crypto-org-chain/cronos/pull/2179) fix(cronos): bound concurrent `ReplayBlock` queries and honor the request context.
 * [#2175](https://github.com/crypto-org-chain/cronos/pull/2175) fix(rpc): guard `TxsResults` length before indexing by block tx position.
```

### go.mod
```diff
@@ -16,8 +16,8 @@ require (
 	github.com/cosmos/cosmos-proto v1.0.0-beta.5
 	github.com/cosmos/cosmos-sdk v0.54.3
 	github.com/cosmos/gogoproto v1.7.2
-	github.com/crypto-org-chain/cronos-store/store v0.0.0-20260518071248-f0453c15e437
-	github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260518071248-f0453c15e437
+	github.com/crypto-org-chain/cronos-store/store v0.0.0-20260923061457-2d12c238d139
+	github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260923061457-2d12c238d139
 	github.com/ethereum/go-ethereum v1.16.9
 	github.com/evmos/ethermint v0.0.0-00010101000000-000000000000
 	github.com/golang/protobuf v1.5.4
@@ -391,9 +391,9 @@ replace (
 	// release/v0.54.x
 	github.com/cosmos/cosmos-sdk => github.com/crypto-org-chain/cosmos-sdk v0.54.4-0.20260805154329-743fc8dc9dbc
 	// master
-	github.com/crypto-org-chain/cronos-store/memiavl => github.com/crypto-org-chain/cronos-store/memiavl v0.0.0-20260807143651-cbef7554cdc3
-	github.com/crypto-org-chain/cronos-store/store => github.com/crypto-org-chain/cronos-store/store v0.0.0-20260807143651-cbef7554cdc3
-	github.com/crypto-org-chain/cronos-store/versiondb => github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260807143651-cbef7554cdc3
+	github.com/crypto-org-chain/cronos-store/memiavl => github.com/crypto-org-chain/cronos-store/memiavl v0.0.0-20260923061457-2d12c238d139
+	github.com/crypto-org-chain/cronos-store/store => github.com/crypto-org-chain/cronos-store/store v0.0.0-20260923061457-2d12c238d139
+	github.com/crypto-org-chain/cronos-store/versiondb => github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260923061457-2d12c238d139
 	// release/v1.16
 	github.com/ethereum/go-ethereum => github.com/crypto-org-chain/go-ethereum v1.10.20-0.20260521015249-663dca6c618e
 
```

### go.sum
```diff
@@ -292,12 +292,12 @@ github.com/crypto-org-chain/cometbft v0.0.0-20260729145603-14b7b93046e3 h1:kw6+G
 github.com/crypto-org-chain/cometbft v0.0.0-20260729145603-14b7b93046e3/go.mod h1:KcZvZTqdLgOisktAoWwwcS2fgO4E110r44KxEGyq8SI=
 github.com/crypto-org-chain/cosmos-sdk v0.54.4-0.20260805154329-743fc8dc9dbc h1:1bj7uwX9gxoxqmWSOQs6+Iz2jse95DRu6w1OQNfiiis=
 github.com/crypto-org-chain/cosmos-sdk v0.54.4-0.20260805154329-743fc8dc9dbc/go.mod h1:d+mzrQ+PV+6t63HomWzLx+OoFeprkjO/b+0ih+LfvIo=
-github.com/crypto-org-chain/cronos-store/memiavl v0.0.0-20260807143651-cbef7554cdc3 h1:LondEiN6lcPCuV2uXPuaUyXPWbjGlzzVp8ljpz0WW1I=
-github.com/crypto-org-chain/cronos-store/memiavl v0.0.0-20260807143651-cbef7554cdc3/go.mod h1:pDMnEFkR+qMEeiTUA07p0Xk4qM1qaCHrHqbR96kJGbQ=
-github.com/crypto-org-chain/cronos-store/store v0.0.0-20260807143651-cbef7554cdc3 h1:DHslvmsZxGAM8p/SoVPhXULQuOGkO/U8Q8zBPmhiXrk=
-github.com/crypto-org-chain/cronos-store/store v0.0.0-20260807143651-cbef7554cdc3/go.mod h1:nbT4YcTZJqW0EY1zNO/o7hx+a0q2hCEjsnZi5vQy2N4=
-github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260807143651-cbef7554cdc3 h1:XvzlhIVxzrjgsHMGRRCsgvkyKw+Y1kGWRa4IaOkvXdQ=
-github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260807143651-cbef7554cdc3/go.mod h1:vNigSKdbXLtFT5wQMaOyLMMXJn3DxL8GRG8cnOZbfUc=
+github.com/crypto-org-chain/cronos-store/memiavl v0.0.0-20260923061457-2d12c238d139 h1:PZhDeIWkyn5O5FnPLip+5peb6smC8/bK2Ufkq06PggQ=
+github.com/crypto-org-chain/cronos-store/memiavl v0.0.0-20260923061457-2d12c238d139/go.mod h1:pDMnEFkR+qMEeiTUA07p0Xk4qM1qaCHrHqbR96kJGbQ=
+github.com/crypto-org-chain/cronos-store/store v0.0.0-20260923061457-2d12c238d139 h1:/lcf+16Wl0okUAkt1vXMbrdivdaptyG1W2EUQJAu4Z4=
+github.com/crypto-org-chain/cronos-store/store v0.0.0-20260923061457-2d12c238d139/go.mod h1:nbT4YcTZJqW0EY1zNO/o7hx+a0q2hCEjsnZi5vQy2N4=
+github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260923061457-2d12c238d139 h1:9mCdXbf9c8wCkJcjGpLBRubxPdLTCrdK9OhYLKYsiWw=
+github.com/crypto-org-chain/cronos-store/versiondb v0.0.0-20260923061457-2d12c238d139/go.mod h1:vNigSKdbXLtFT5wQMaOyLMMXJn3DxL8GRG8cnOZbfUc=
 github.com/crypto-org-chain/ethermint v0.22.1-0.20260922081214-84a631b06a9b h1:IxSW+yAPkIo8mTesgP261SuQYcWyVI2Q4046fM4GvJw=
 github.com/crypto-org-chain/ethermint v0.22.1-0.20260922081214-84a631b06a9b/go.mod h1:dnk62oZ22GUvyW8w56BTEqa20Nc8Rl+s6nkAEo1OAU0=
 github.com/crypto-org-chain/go-ethereum v1.10.20-0.20260521015249-663dca6c618e h1:ftyRRWDiXKWsnp3PxLNbfVLzrqkx+aDNZdkPconawWk=
```

### gomod2nix.toml
```diff
@@ -302,15 +302,15 @@ schema = 3
     version = "v0.0.29"
     hash = "sha256-QP39Y1YMGWQSIAaD92s6LVLERgwh+5004a7U3flUTU8="
   [mod."github.com/crypto-org-chain/cronos-store/memiavl"]
-    version = "v0.0.0-20260807143651-cbef7554cdc3"
-    hash = "sha256-7AdHQjSa6M6gESfKdXAwJLM+ALgtxWqLkKYIlsjX2Tk="
+    version = "v0.0.0-20260923061457-2d12c238d139"
+    hash = "sha256-83AiVbEB1COpkUmRvLLGW9J87NSBjfR29ALlG4iuz0w="
     replaced = "github.com/crypto-org-chain/cronos-store/memiavl"
   [mod."github.com/crypto-org-chain/cronos-store/store"]
-    version = "v0.0.0-20260807143651-cbef7554cdc3"
+    version = "v0.0.0-20260923061457-2d12c238d139"
     hash = "sha256-N0TYukNwMH66J+i530opwuzBJWzfLrixgM1pChgKK0w="
     replaced = "github.com/crypto-org-chain/cronos-store/store"
   [mod."github.com/crypto-org-chain/cronos-store/versiondb"]
-    version = "v0.0.0-20260807143651-cbef7554cdc3"
+    version = "v0.0.0-20260923061457-2d12c238d139"
     hash = "sha256-SIIJ6Is7MccaSzlGA4Gz6xo1DWHWYRoEG9lkFsgqDxs="
     replaced = "github.com/crypto-org-chain/cronos-store/versiondb"
   [mod."github.com/danieljoos/wincred"]
@@ -412,8 +412,8 @@ schema = 3
     version = "v0.6.1"
     hash = "sha256-+gUGmdR/QOsB9qKESLrsbq6tK2VssNT/kDbRFpgrZL4="
   [mod."github.com/go-logr/logr"]
-    version = "v1.4.3"
-    hash = "sha256-Nnp/dEVNMxLp3RSPDHZzGbI8BkSNuZMX0I0cjWKXXLA="
+    version = "v1.4.4"
+    hash = "sha256-q9HX9aelONTLsywyLY4Wc5UYCK+wG0FbSzFWisCYiIA="
   [mod."github.com/go-logr/stdr"]
     version = "v1.2.2"
     hash = "sha256-rRweAP7XIb4egtT1f2gkz4sYOu7LDHmcJ5iNsJUd0sE="
@@ -487,8 +487,8 @@ schema = 3
     version = "v1.16.0"
     hash = "sha256-wLymGic7wZ6fSiBYDAaGqnQ9Ste1fUWeqXeolZXCHvI="
   [mod."github.com/grpc-ecosystem/grpc-gateway/v2"]
-    version = "v2.28.0"
-    hash = "sha256-QeWb6jN6noeGPCzECgpUSb9YX9LzvKGwImEuX+A03gs="
+    version = "v2.29.0"
+    hash = "sha256-a/J/iffTIqbKXIBGGKfPIjgfyb2F05jw3Au8f1q6yEk="
   [mod."github.com/gsterjov/go-libsecret"]
     version = "v0.0.0-20161001094733-a6f4afe4910c"
     hash = "sha256-Z5upjItPU9onq5t7VzhdQFp13lMJrSiE3gNRapuK6ic="
@@ -721,8 +721,8 @@ schema = 3
     version = "v2.2.12"
     hash = "sha256-NLz6Aa6sg8sre7yKoiE0TdOtzyDxlnkYldByveCUNww="
   [mod."github.com/pion/dtls/v3"]
-    version = "v3.1.2"
-    hash = "sha256-eWgXdBDNk/9Tpi5M5dEq0lAWYWU+tbnDUVaiQyQTjFU="
+    version = "v3.1.4"
+    hash = "sha256-WAy5D9ccKoK0Afn4vxNqsX5iLpq19RVhpq9U+hU4W4w="
   [mod."github.com/pion/ice/v4"]
     version = "v4.0.10"
     hash = "sha256-Yeq0XUDI264wOPhHWajoW2K3trwmyBOzHhzs/5uk5ic="
@@ -757,17 +757,17 @@ schema = 3
     version = "v2.0.0"
     hash = "sha256-ptqO5Q2UG6rm4AiAJsJ44gycR1OzFRtgNSns2GrQ/gY="
   [mod."github.com/pion/stun/v3"]
-    version = "v3.1.1"
-    hash = "sha256-RsBz18rPiiVo4133WFOqmgl7Mz8SD3EZhhoF6n+Og/s="
+    version = "v3.1.5"
+    hash = "sha256-Cm996Vwf3Bn0qsKIRZy86svZXn/O5az7YDGENyOW30o="
   [mod."github.com/pion/transport/v2"]
     version = "v2.2.10"
     hash = "sha256-YTMWnXUqAsoigVg+D6xfEFJcXCwU7JYEJWQNG167Nr8="
   [mod."github.com/pion/transport/v3"]
     version = "v3.0.7"
     hash = "sha256-b/MToefdk4m28vw+3G4SECEbWP/jSBZRC5fDneaIvAk="
   [mod."github.com/pion/transport/v4"]
-    version = "v4.0.1"
-    hash = "sha256-hDHt5UUtdVB6EQuWjIg1s5PPyUTq2gY5sUpydVe87Ak="
+    version = "v4.0.2"
+    hash = "sha256-XOZrl9gY6H2+LtKwwhfFZ8f/FyHo+8no6f64lvcWizQ="
   [mod."github.com/pion/turn/v4"]
     version = "v4.0.2"
     hash = "sha256-kFJImdexwp3AVlJuaIGdnRAJilzpgt1TGVpjuAAEq7M="
@@ -935,8 +935,8 @@ schema = 3
     version = "v1.2.1"
     hash = "sha256-73bFYhnxNf4SfeQ52ebnwOWywdQbqc9lWawCcSgofvE="
   [mod."go.opentelemetry.io/contrib/bridges/otelslog"]
-    version = "v0.18.0"
-    hash = "sha256-m1iSWb89HFOPP1I8Zqb+p85ZMRrdlyAM9x6FjcW7DQ4="
+    version = "v0.20.0"
+    hash = "sha256-eN8qaSqpK7Q+Us70fNPfKftHQuVC2FCQMzDtYWlUxAw="
   [mod."go.opentelemetry.io/contrib/detectors/gcp"]
     version = "v1.44.0"
     hash = "sha256-dp+EQTl8DCYVrRKEJ/IpRMUomgIRx/M0z2LkeCctwiY="
@@ -971,59 +971,59 @@ schema = 3
     version = "v1.43.0"
     hash = "sha256-oJUlEiywS8JXOY0A/BUdrxBy70i904YrsmrbtMc1hbU="
   [mod."go.opentelemetry.io/otel"]
-    version = "v1.44.0"
-    hash = "sha256-XTGV9RjOIKyWrrgXJ32IA59lovxXqSeRrpcpC1FAFZA="
+    version = "v1.45.0"
+    hash = "sha256-ORef6E6hxMrpVU8b+4vh311bMbv2zGbYAIJ9ZE8gXvc="
   [mod."go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploggrpc"]
-    version = "v0.19.0"
-    hash = "sha256-4R/vtaw7tAi8S+wCa8a8U3bAWOT9DXIFdUT9KWfysOc="
+    version = "v0.21.0"
+    hash = "sha256-FGpQp6G7uHfntlCABqpwUycz4yeiRz6m+X3GqWzBUJY="
   [mod."go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploghttp"]
-    version = "v0.19.0"
-    hash = "sha256-fPT9B5yAIEXYVGBi5gcc7emErpKGUZzY46TV68wCWJ0="
+    version = "v0.21.0"
+    hash = "sha256-+suZDi6pwZ5WWE7jnYwap5nxb2e8TWjFAC2+HBSNZ8w="
   [mod."go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc"]
     version = "v1.43.0"
     hash = "sha256-Ywq1bOmyuEY2FQ+0AqB39996DnGohg8UtFR/aJxRYSc="
   [mod."go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetrichttp"]
     version = "v1.43.0"
     hash = "sha256-w0aHW8rhDy5W8MuL7yekpJnEFxlIIjn7v9jyG4Jdql0="
   [mod."go.opentelemetry.io/otel/exporters/otlp/otlptrace"]
-    version = "v1.43.0"
-    hash = "sha256-caYRUaQ4DZGYtcUtH5kEkWXezDI4/vZRpUXpet3tQlg="
+    version = "v1.45.0"
+    hash = "sha256-+q9AqsCDxlrXTmELo5IJwR5yNiHzCk/dk7mtxxmqCf8="
   [mod."go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"]
-    version = "v1.43.0"
-    hash = "sha256-eb10xx3JrjEG+A6S0QUtS9/LKQm/HeJIjy4TippGiOM="
+    version = "v1.45.0"
+    hash = "sha256-fqrhkxeR2Go6sA9W9xKRYpXQfHBZ78/7MVWnyuRpWSU="
   [mod."go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"]
-    version = "v1.43.0"
-    hash = "sha256-wvXfMOb3dIVtNDrsxO+wlH3BJwN70t3p0X2EV/ubPjQ="
+    version = "v1.45.0"
+    hash = "sha256-GT6dy7rdPY6WK3aByofcuWkMHuT5IhULkiisuzStqag="
   [mod."go.opentelemetry.io/otel/exporters/stdout/stdoutlog"]
-    version = "v0.19.0"
-    hash = "sha256-pg2uKuO/qz8yTE8b1gTBzCq7i8/1Qd+ouB6zeuV/mHo="
+    version = "v0.21.0"
+    hash = "sha256-+vdEoq4bFFXbEC7HZhio71NgwE/CfiekllYq60Yho8c="
   [mod."go.opentelemetry.io/otel/exporters/stdout/stdoutmetric"]
     version = "v1.43.0"
     hash = "sha256-ygULgA8spJJotC/uog+xygtrJ67xXtUr3OJtKHiCq7M="
   [mod."go.opentelemetry.io/otel/exporters/stdout/stdouttrace"]
     version = "v1.43.0"
     hash = "sha256-ILr+FPHHhnLqVRNRlbLkKQE78jSZ/Ow7h9XE3G4LaaI="
   [mod."go.opentelemetry.io/otel/log"]
-    version = "v0.19.0"
-    hash = "sha256-bxaeA+aHA2VRrl4hfzomoadJyq34e6pzUvW9BLTtC/o="
+    version = "v0.21.0"
+    hash = "sha256-c4QuZ3aWeIJx0aB4GKnvQP+ah3Vh3u2rooEef6MBx3E="
   [mod."go.opentelemetry.io/otel/metric"]
-    version = "v1.44.0"
-    hash = "sha256-e8dVyRoavby/YG7aH2T05IhWHlLvwnMHyPhelAS1mCQ="
+    version = "v1.45.0"
+    hash = "sha256-Ec/v1Ghb8Ohb1NsdYQ6juggl/wJMrVA6ktPRPczGWMQ="
   [mod."go.opentelemetry.io/otel/sdk"]
-    version = "v1.44.0"
-    hash = "sha256-rNqJXr5P2f5Qgllp/3E5Rm5lqt1kBhxHXppT5dXw5Cw="
+    version = "v1.45.0"
+    hash = "sha256-VoyRt1cLW8apITGla1K1fqbSyJyRPr53+R3iisreE+4="
   [mod."go.opentelemetry.io/otel/sdk/log"]
-    version = "v0.19.0"
-    hash = "sha256-mV2lp63Qi6THZYNmWEBo6puRFdslx3meMC+Sv7vs3iU="
+    version = "v0.21.0"
+    hash = "sha256-FI+YN8zJXGNWAYWxNxozl6GnFl8ApI+jnXa4bEjtVyQ="
   [mod."go.opentelemetry.io/otel/sdk/metric"]
-    version = "v1.44.0"
-    hash = "sha256-9OJi3uCRMdCo0d5YZjJnPCveQ9JNifNoOUBOEPtNBBE="
+    version = "v1.45.0"
+    hash = "sha256-sjqCSECo+FNQ6IplnRrh2rFdCbYdS9/B6LgoxVjCNIo="
   [mod."go.opentelemetry.io/otel/trace"]
-    version = "v1.44.0"
-    hash = "sha256-69HorWRTLLzAHRgLe4nPp13qJthb3qp7RU7c0Y9qV/c="
+    version = "v1.45.0"
+    hash = "sha256-LKrsYVdfPEzxXPEFSapjGIiw2e1C4Yq5HXtoYrN4FIY="
   [mod."go.opentelemetry.io/proto/otlp"]
-    version = "v1.10.0"
-    hash = "sha256-IEnbR38ucFLTcuC2FA+gRvZNq2loUqXgDskSqP3+LUM="
+    version = "v1.11.0"
+    hash = "sha256-jBcVUiab9mWgLmPsrCYK7sC2j15AJ47QJM4prnqGGkE="
   [mod."go.uber.org/dig"]
     version = "v1.19.0"
     hash = "sha256-/27soFu058DqVt8F4Yoq987lwqS+iz5n2bMGawclrfI="
@@ -1049,56 +1049,56 @@ schema = 3
     version = "v0.26.0"
     hash = "sha256-xssXQRlEa2O2Dv4lfLsshYIn2r67nhBPOdvL58MnEXo="
   [mod."golang.org/x/crypto"]
-    version = "v0.53.0"
-    hash = "sha256-TWcccM4d5t0ZbDyHXEm4elxKk5uzlo29i85lVHSZcNw="
+    version = "v0.55.0"
+    hash = "sha256-99uV/ESeqhaDEwqbXxDpePuwzO0JoEHGhqZXZVHq/H4="
   [mod."golang.org/x/exp"]
     version = "v0.0.0-20260508232706-74f9aab9d74a"
     hash = "sha256-SO8xfkN0mmZICYCvlH0jZbWmuFT30kvMZSkGZfmJQWQ="
   [mod."golang.org/x/mod"]
-    version = "v0.37.0"
-    hash = "sha256-dspScRv3KO4nytvjavhNO2b03P4UtiJQyWVGuEy9OUk="
+    version = "v0.38.0"
+    hash = "sha256-BpKfvsmb7ecEDvTBKx9ZHauxoWRkOAZCqg4BrHM2/S0="
   [mod."golang.org/x/net"]
-    version = "v0.56.0"
-    hash = "sha256-JUORjxDZqZanYWo2yunaDpQ2/zvHiFb0TnF1Jw6D+30="
+    version = "v0.58.0"
+    hash = "sha256-fDOkQJXURrbq2dBGa91bCUsXknCZlo3ru2JIofSOGRo="
   [mod."golang.org/x/oauth2"]
     version = "v0.36.0"
     hash = "sha256-evS7WkMrpgonmTcqtWFpC5rSKZN8O+vnAhNUs1MS9kw="
   [mod."golang.org/x/sync"]
-    version = "v0.21.0"
-    hash = "sha256-2n7PVb1krz7UpnXYGVmCrxV0fZBnjQdVVt6eVudEPYY="
+    version = "v0.22.0"
+    hash = "sha256-VZjl0fAM0p/nI81zh+pdBjzxFupx0UcKYXBBpL2ZS7k="
   [mod."golang.org/x/sys"]
-    version = "v0.46.0"
-    hash = "sha256-NzRXMSEk6upeudJvUEPVnw6clJ3d8UdC/vdfANWAc8g="
+    version = "v0.47.0"
+    hash = "sha256-TpbRyWWqHjddP6QzUgAbaLd2EE0S+GYNRUIDJd18r98="
   [mod."golang.org/x/telemetry"]
-    version = "v0.0.0-20260625142307-59b4966ccb57"
-    hash = "sha256-NymRmhUJZd33Ziexww/0pMgnuioRXcykAQcICdq8Qps="
+    version = "v0.0.0-20260708182218-49f421fb7959"
+    hash = "sha256-Nbj0aAfoPlOnAMvyqyjW5YhQjcnjLfpScna4yIRhTHk="
   [mod."golang.org/x/term"]
-    version = "v0.44.0"
-    hash = "sha256-nzbvOgvGRbx1qpq1rbk7b6zNsNeNj8mOGoyZLtnzq3w="
+    version = "v0.45.0"
+    hash = "sha256-vPBeJkepEZ1D9k4oaV20IuQlVmfAFv15KQgnhl9MNgw="
   [mod."golang.org/x/text"]
-    version = "v0.39.0"
-    hash = "sha256-jQR8eNeC6HIFxRdEbF3EAUcoCOvpSJ/latXSqt5w0YA="
+    version = "v0.41.0"
+    hash = "sha256-22nHcolG87qSPahT2Ey8S5iGlCLAglE9ObYXO6XZ3ZY="
   [mod."golang.org/x/time"]
     version = "v0.15.0"
     hash = "sha256-5D24A65wn7k93Jj3+918UKjB9ccmGHPBEqjD2XDB92E="
   [mod."golang.org/x/tools"]
-    version = "v0.47.0"
-    hash = "sha256-LyCNqEb/Jm94O6gaM01vXSHP9Yw/Cw0qVWXGxhCgwzo="
+    version = "v0.48.0"
+    hash = "sha256-9cRNUaup6fexA5S1zc+Ic3aaoxAgKWntyMJ2xaOdiP8="
   [mod."google.golang.org/api"]
     version = "v0.276.0"
     hash = "sha256-qXHX3iYmJD3Pb1vaCaTwSoqvTdbnNljndShDM8sSJUM="
   [mod."google.golang.org/genproto"]
     version = "v0.0.0-20260511170946-3700d4141b60"
     hash = "sha256-vMFDiE/UeGPXvYfcCp6KL/TLHuL0+CxXnZbgfUgXkss="
   [mod."google.golang.org/genproto/googleapis/api"]
-    version = "v0.0.0-20260526163538-3dc84a4a5aaa"
-    hash = "sha256-XwBCYWKK47hTvTNUl8HenRcbzU5xIYhRfPfNypUU1Ps="
+    version = "v0.0.0-20260803160001-6ac0973c030d"
+    hash = "sha256-cECK1WQFTL6TgViX2EOA5honMcFueFP0omL2PmYIEd0="
   [mod."google.golang.org/genproto/googleapis/rpc"]
-    version = "v0.0.0-20260526163538-3dc84a4a5aaa"
+    version = "v0.0.0-20260803160001-6ac0973c030d"
     hash = "sha256-ldJTTb7hhj1mdmzTn9IEkQVwCoj3KRlENZtUSEKHABU="
   [mod."google.golang.org/grpc"]
-    version = "v1.83.1"
-    hash = "sha256-FpEi28U8I4/pzzfS+Gv4PySLcxkjVTy1pqtRlEDZJ54="
+    version = "v1.83.2"
+    hash = "sha256-q5VtdeJvWM7kbIvui8ncNV/+Rm+d0y/b6XkNN0/u1is="
   [mod."google.golang.org/protobuf"]
     version = "v1.36.11"
     hash = "sha256-7W+6jntfI/awWL3JP6yQedxqP5S9o3XvPgJ2XxxsIeE="
```
