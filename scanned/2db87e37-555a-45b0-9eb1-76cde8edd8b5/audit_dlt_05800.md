# [?] Cosmwasm Cherry security patch (#4954) (#5404)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2023-06-06
Source: https://github.com/osmosis-labs/osmosis/commit/314c771b727257ff069483d8732026effafa7add
Type: security-commit

## Details
Cosmwasm Cherry security patch (#4954) (#5404)

* Cosmwasm Cherry security patch (#4954)

* upgrade wasmvm

* get the proper version of wasmvm

* updated changelog

* experimenting with moving arch out of the command

* ensure correct package is grepped

* remove wasmd cache

* handle error

* lint

## Patch
### CHANGELOG.md
```diff
@@ -42,6 +42,10 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ## [Unreleased]
 
+### Security
+
+* Upgraded wasmvm to 1.2.3 in response to [CWA-2023-002](https://github.com/CosmWasm/advisories/blob/main/CWAs/CWA-2023-002.md)
+
 ### Features
   * [#5354](https://github.com/osmosis-labs/osmosis/pull/5354) implement x/cosmwasmpool module.
   * [#4659](https://github.com/osmosis-labs/osmosis/pull/4659) implement AllPools query in x/poolmanager.
```

### Dockerfile
```diff
@@ -25,12 +25,12 @@ RUN --mount=type=cache,target=/root/.cache/go-build \
     go mod download
 
 # Cosmwasm - Download correct libwasmvm version
-RUN WASMVM_VERSION=$(go list -m github.com/CosmWasm/wasmvm | cut -d ' ' -f 2) && \
-    wget https://github.com/CosmWasm/wasmvm/releases/download/$WASMVM_VERSION/libwasmvm_muslc.$(uname -m).a \
+RUN ARCH=$(uname -m) && WASMVM_VERSION=$(go list -m github.com/CosmWasm/wasmvm | sed 's/.* //') && \
+    wget https://github.com/CosmWasm/wasmvm/releases/download/$WASMVM_VERSION/libwasmvm_muslc.$ARCH.a \
         -O /lib/libwasmvm_muslc.a && \
     # verify checksum
     wget https://github.com/CosmWasm/wasmvm/releases/download/$WASMVM_VERSION/checksums.txt -O /tmp/checksums.txt && \
-    sha256sum /lib/libwasmvm_muslc.a | grep $(cat /tmp/checksums.txt | grep $(uname -m) | cut -d ' ' -f 1)
+    sha256sum /lib/libwasmvm_muslc.a | grep $(cat /tmp/checksums.txt | grep libwasmvm_muslc.$ARCH | cut -d ' ' -f 1)
 
 # Copy the remaining files
 COPY . .
```

### app/app.go
```diff
@@ -9,6 +9,8 @@ import (
 	"reflect"
 	"strings"
 
+	store "github.com/cosmos/cosmos-sdk/store/types"
+
 	wasmtypes "github.com/CosmWasm/wasmd/x/wasm/types"
 
 	vestingtypes "github.com/cosmos/cosmos-sdk/x/auth/vesting/types"
@@ -139,6 +141,7 @@ type OsmosisApp struct {
 
 	mm           *module.Manager
 	configurator module.Configurator
+	homePath     string
 }
 
 // init sets DefaultNodeHome to default osmosisd install location.
@@ -204,6 +207,7 @@ func NewOsmosisApp(
 		invCheckPeriod:    invCheckPeriod,
 	}
 
+	app.homePath = homePath
 	wasmDir := filepath.Join(homePath, "wasm")
 	wasmConfig, err := wasm.ReadWasmConfig(appOpts)
 	// Uncomment this for debugging contracts. In the future this could be made into a param passed by the tests
@@ -438,13 +442,32 @@ func (app *OsmosisApp) setupUpgradeStoreLoaders() {
 		return
 	}
 
+	currentHeight := app.CommitMultiStore().LastCommitID().Version
+
+	if upgradeInfo.Height == currentHeight+1 {
+		app.customPreUpgradeHandler(upgradeInfo)
+	}
+
 	for _, upgrade := range Upgrades {
 		if upgradeInfo.Name == upgrade.UpgradeName {
 			app.SetStoreLoader(upgradetypes.UpgradeStoreLoader(upgradeInfo.Height, &upgrade.StoreUpgrades))
 		}
 	}
 }
 
+func (app *OsmosisApp) customPreUpgradeHandler(upgradeInfo store.UpgradeInfo) {
+	switch upgradeInfo.Name {
+	case "v16":
+		// v16 upgrade handler
+		fmt.Println("Running v16 pre-upgrade handler")
+		// remove the wasm cache for cosmwasm cherry https://github.com/CosmWasm/advisories/blob/main/CWAs/CWA-2023-002.md#wasm-module-cache-issue
+		err := os.RemoveAll(app.homePath + "/wasm/wasm/cache")
+		if err != nil {
+			panic(err)
+		}
+	}
+}
+
 func (app *OsmosisApp) setupUpgradeHandlers() {
 	for _, upgrade := range Upgrades {
 		app.UpgradeKeeper.SetUpgradeHandler(
```

### go.mod
```diff
@@ -23,7 +23,7 @@ require (
 	github.com/osmosis-labs/osmosis/osmomath v0.0.3-dev.0.20230516205127-c213fddde069
 	github.com/osmosis-labs/osmosis/osmoutils v0.0.0-20230605194623-ad924fbdd9b0
 	github.com/osmosis-labs/osmosis/x/epochs v0.0.0-20230328024000-175ec88e4304
-	github.com/osmosis-labs/osmosis/x/ibc-hooks v0.0.0-20230331072320-5d6f6cfa2627
+	github.com/osmosis-labs/osmosis/x/ibc-hooks v0.0.0-20230602130523-f9a94d8bbd10
 	github.com/pkg/errors v0.9.1
 	github.com/rakyll/statik v0.1.7
 	github.com/spf13/cast v1.5.1
@@ -56,12 +56,11 @@ require (
 	github.com/curioswitch/go-reassign v0.2.0 // indirect
 	github.com/docker/distribution v2.8.2+incompatible // indirect
 	github.com/felixge/httpsnoop v1.0.2 // indirect
-	github.com/go-playground/universal-translator v0.18.0 // indirect
+	github.com/go-playground/locales v0.14.0 // indirect
 	github.com/gogo/gateway v1.1.0 // indirect
 	github.com/google/btree v1.1.2 // indirect
 	github.com/junk1tm/musttag v0.5.0 // indirect
 	github.com/kkHAIKE/contextcheck v1.1.4 // indirect
-	github.com/leodido/go-urn v1.2.1 // indirect
 	github.com/maratori/testableexamples v1.0.0 // indirect
 	github.com/nunnatsa/ginkgolinter v0.9.0 // indirect
 	github.com/regen-network/cosmos-proto v0.3.1 // indirect
@@ -315,6 +314,8 @@ require (
 replace (
 	// osmosis-patched wasmd.
 	github.com/CosmWasm/wasmd => github.com/osmosis-labs/wasmd v0.31.0-osmo-v16
+	// Security patch for wasmvm. See https://github.com/CosmWasm/advisories/blob/main/CWAs/CWA-2023-002.md
+	github.com/CosmWasm/wasmvm => github.com/CosmWasm/wasmvm v1.2.3
 	// dragonberry
 	github.com/confio/ics23/go => github.com/cosmos/cosmos-sdk/ics23/go v0.8.0
 	// Our cosmos-sdk branch is:  https://github.com/osmosis-labs/cosmos-sdk, current branch: v16.x. Direct commit link: https://github.com/osmosis-labs/cosmos-sdk/commit/93d9d4851b92bcbc1ede8c031ca1559b35ecc708
```

### go.sum
```diff
@@ -70,8 +70,8 @@ github.com/BurntSushi/toml v1.2.1/go.mod h1:CxXYINrC8qIiEnFrOxCa7Jy5BFHlXnUU2pbi
 github.com/BurntSushi/xgb v0.0.0-20160522181843-27f122750802/go.mod h1:IVnqGOEym/WlBOVXweHU+Q+/VP0lqqI8lqeDx9IjBqo=
 github.com/ChainSafe/go-schnorrkel v0.0.0-20200405005733-88cbf1b4c40d h1:nalkkPQcITbvhmL4+C4cKA87NW0tfm3Kl9VXRoPywFg=
 github.com/ChainSafe/go-schnorrkel v0.0.0-20200405005733-88cbf1b4c40d/go.mod h1:URdX5+vg25ts3aCh8H5IFZybJYKWhJHYMTnf+ULtoC4=
-github.com/CosmWasm/wasmvm v1.2.1 h1:si0tRsRDdUShV0k51Wn6zRKlmj3/WWP9Yr4cLmDTf+8=
-github.com/CosmWasm/wasmvm v1.2.1/go.mod h1:vW/E3h8j9xBQs9bCoijDuawKo9kCtxOaS8N8J7KFtkc=
+github.com/CosmWasm/wasmvm v1.2.3 h1:OKYlobwmVGbl0eSn0mXoAAjE5hIuXnQCLPjbNd91sVY=
+github.com/CosmWasm/wasmvm v1.2.3/go.mod h1:vW/E3h8j9xBQs9bCoijDuawKo9kCtxOaS8N8J7KFtkc=
 github.com/DATA-DOG/go-sqlmock v1.3.3/go.mod h1:f/Ixk793poVmq4qj/V1dPUg2JEAKC73Q5eFN3EC/SaM=
 github.com/DataDog/datadog-go v3.2.0+incompatible/go.mod h1:LButxg5PwREeZtORoXG3tL4fMGNddJ+vMq1mwgfaqoQ=
 github.com/DataDog/zstd v1.5.0/go.mod h1:g4AWEaM3yOg3HYfnJ3YIawPnVdXJh9QME85blwSAmyw=
@@ -407,7 +407,6 @@ github.com/go-playground/locales v0.14.0 h1:u50s323jtVGugKlcYeyzC0etD1HifMjqmJqb
 github.com/go-playground/locales v0.14.0/go.mod h1:sawfccIbzZTqEDETgFXqTho0QybSa7l++s0DH+LDiLs=
 github.com/go-playground/universal-translator v0.17.0/go.mod h1:UkSxE5sNxxRwHyU+Scu5vgOQjsIJAF8j9muTVoKLVtA=
 github.com/go-playground/universal-translator v0.18.0 h1:82dyy6p4OuJq4/CByFNOn/jYrnRPArHwAcmLoJZxyho=
-github.com/go-playground/universal-translator v0.18.0/go.mod h1:UvRDBj+xPUEGrFYl+lu/H90nyDXpg0fqeB/AQUGNTVA=
 github.com/go-playground/validator/v10 v10.2.0/go.mod h1:uOYAAleCW8F/7oMFd6aG0GOhaH6EGOAJShg8Id5JGkI=
 github.com/go-playground/validator/v10 v10.11.1 h1:prmOlTVv+YjZjmRmNSF3VmspqJIxJWXmqUsHwfTRRkQ=
 github.com/go-sourcemap/sourcemap v2.1.3+incompatible/go.mod h1:F8jJfvm2KbVjc5NqelyYJmf/v5J0dwNLS2mL4sNA1Jg=
@@ -771,7 +770,6 @@ github.com/ldez/tagliatelle v0.4.0/go.mod h1:mNtTfrHy2haaBAw+VT7IBV6VXBThS7TCreY
 github.com/leanovate/gopter v0.2.9/go.mod h1:U2L/78B+KVFIx2VmW6onHJQzXtFb+p5y3y2Sh+Jxxv8=
 github.com/leodido/go-urn v1.2.0/go.mod h1:+8+nEpDfqqsY+g338gtMEUOtuK+4dEMhiQEgxpxOKII=
 github.com/leodido/go-urn v1.2.1 h1:BqpAaACuzVSgi/VLzGZIobT2z4v53pjosyNd9Yv6n/w=
-github.com/leodido/go-urn v1.2.1/go.mod h1:zt4jvISO2HfUBqxjfIshjdMTYS56ZS/qv49ictyFfxY=
 github.com/leonklingele/grouper v1.1.1 h1:suWXRU57D4/Enn6pXR0QVqqWWrnJ9Osrz+5rjt8ivzU=
 github.com/leonklingele/grouper v1.1.1/go.mod h1:uk3I3uDfi9B6PeUjsCKi6ndcf63Uy7snXgR4yDYQVDY=
 github.com/lib/pq v1.0.0/go.mod h1:5WUZQaWbwv1U+lTReE5YruASi9Al49XbQIvNi/34Woo=
@@ -949,8 +947,8 @@ github.com/osmosis-labs/osmosis/osmoutils v0.0.0-20230605194623-ad924fbdd9b0 h1:
 github.com/osmosis-labs/osmosis/osmoutils v0.0.0-20230605194623-ad924fbdd9b0/go.mod h1:Y/K8fW4DfXn9mxU+49bASVKfNjkX/0TshGolJRYnej0=
 github.com/osmosis-labs/osmosis/x/epochs v0.0.0-20230328024000-175ec88e4304 h1:RIrWLzIiZN5Xd2JOfSOtGZaf6V3qEQYg6EaDTAkMnCo=
 github.com/osmosis-labs/osmosis/x/epochs v0.0.0-20230328024000-175ec88e4304/go.mod h1:yPWoJTj5RKrXKUChAicp+G/4Ni/uVEpp27mi/FF/L9c=
-github.com/osmosis-labs/osmosis/x/ibc-hooks v0.0.0-20230331072320-5d6f6cfa2627 h1:A0SwZgp4bmJFbivYJc8mmVhMjrr3EdUZluBYFke11+w=
-github.com/osmosis-labs/osmosis/x/ibc-hooks v0.0.0-20230331072320-5d6f6cfa2627/go.mod h1:w+bI52bxyC5RwmymC1cK3pYzSNvmGAe5uOzqUzj9suU=
+github.com/osmosis-labs/osmosis/x/ibc-hooks v0.0.0-20230602130523-f9a94d8bbd10 h1:XrES5AHZMZ/Y78boW35PTignkhN9h8VvJ1sP8EJDIu8=
+github.com/osmosis-labs/osmosis/x/ibc-hooks v0.0.0-20230602130523-f9a94d8bbd10/go.mod h1:Ln6CKcXg/CJLSBE6Fd96/MIKPyA4iHuQTKSbl9q7vYo=
 github.com/osmosis-labs/wasmd v0.31.0-osmo-v16 h1:X747cZYdnqc/+RV48iPVeGprpVb/fUWSaKGsZUWrdbg=
 github.com/osmosis-labs/wasmd v0.31.0-osmo-v16/go.mod h1:Rf8zW/GgBQyFRRB4s62VQHWA6sTlMFSjoDQQpoq64iI=
 github.com/otiai10/copy v1.2.0/go.mod h1:rrF5dJ5F0t/EWSYODDu4j9/vEeYHMkc8jt0zJChqQWw=
```

### x/ibc-hooks/go.mod
```diff
@@ -140,8 +140,9 @@ require (
 
 replace (
 	// osmosis-patched wasmd
-	// ToDo: replace the commit hash with v0.31.0-osmo-v15 once the version is tagged
 	github.com/CosmWasm/wasmd => github.com/osmosis-labs/wasmd v0.31.0-osmo-v16
+	// Security patch for wasmvm. See https://github.com/CosmWasm/advisories/blob/main/CWAs/CWA-2023-002.md
+	github.com/CosmWasm/wasmvm => github.com/CosmWasm/wasmvm v1.2.3
 	// dragonberry
 	github.com/confio/ics23/go => github.com/cosmos/cosmos-sdk/ics23/go v0.8.0
 	// Our cosmos-sdk branch is:  https://github.com/osmosis-labs/cosmos-sdk, current branch: v16.x. Direct commit link: https://github.com/osmosis-labs/cosmos-sdk/commit/93d9d4851b92bcbc1ede8c031ca1559b35ecc708
```
