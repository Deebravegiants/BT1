# [?] fix: packet forward middleware panic when transferring tokens with 10^18 denom (#262)

## Summary
Severity: Unknown
Chain: Dymension
Component: dymensionxyz/dymension
Published: 2023-06-14
Source: https://github.com/dymensionxyz/dymension/commit/bedea9de15753d6b0b220f461d427bac2a32753a
Type: security-commit

## Details
fix: packet forward middleware panic when transferring tokens with 10^18 denom (#262)

## Patch
### app/app.go
```diff
@@ -251,7 +251,7 @@ type App struct {
 	EvidenceKeeper   evidencekeeper.Keeper
 	TransferKeeper   ibctransferkeeper.Keeper
 	FeeGrantKeeper   feegrantkeeper.Keeper
-	RouterKeeper     routerkeeper.Keeper
+	RouterKeeper     *routerkeeper.Keeper
 
 	// make scoped keepers public for test purposes
 	ScopedIBCKeeper      capabilitykeeper.ScopedKeeper
@@ -491,16 +491,18 @@ func New(
 		app.IBCKeeper.ChannelKeeper,
 		app.DistrKeeper,
 		app.BankKeeper,
+		app.IBCKeeper.ChannelKeeper,
 	)
 
 	transferModule := transfer.NewAppModule(app.TransferKeeper)
-	transferIBCModule := transfer.NewIBCModule(app.TransferKeeper)
-	routerModule := router.NewAppModule(app.RouterKeeper, transferIBCModule, 0,
-		routerkeeper.DefaultForwardTransferPacketTimeoutTimestamp, routerkeeper.DefaultRefundTransferPacketTimeoutTimestamp)
+
+	var transferStack ibcporttypes.IBCModule
+	transferStack = transfer.NewIBCModule(app.TransferKeeper)
+	transferStack = router.NewIBCMiddleware(transferStack, app.RouterKeeper, 0, routerkeeper.DefaultForwardTransferPacketTimeoutTimestamp, routerkeeper.DefaultRefundTransferPacketTimeoutTimestamp)
 
 	// Create static IBC router, add transfer route, then set and seal it
 	ibcRouter := ibcporttypes.NewRouter()
-	ibcRouter.AddRoute(ibctransfertypes.ModuleName, routerModule)
+	ibcRouter.AddRoute(ibctransfertypes.ModuleName, transferStack)
 	// this line is used by starport scaffolding # ibc/app/router
 	app.IBCKeeper.SetRouter(ibcRouter)
 
@@ -534,7 +536,7 @@ func New(
 		evidence.NewAppModule(app.EvidenceKeeper),
 		ibcModule,
 		params.NewAppModule(app.ParamsKeeper),
-		routerModule,
+		router.NewAppModule(app.RouterKeeper),
 		transferModule,
 		rollappModule,
 		sequencerModule,
@@ -649,7 +651,7 @@ func New(
 		evidence.NewAppModule(app.EvidenceKeeper),
 		ibcModule,
 		transferModule,
-		routerModule,
+		router.NewAppModule(app.RouterKeeper),
 		rollappModule,
 		sequencerModule,
 		ircModule,
```

### go.mod
```diff
@@ -12,11 +12,11 @@ require (
 	github.com/grpc-ecosystem/grpc-gateway v1.16.0
 	github.com/ignite/cli v0.23.0
 	github.com/spf13/cast v1.5.0
-	github.com/spf13/cobra v1.5.0
+	github.com/spf13/cobra v1.6.1
 	github.com/spf13/pflag v1.0.5
-	github.com/strangelove-ventures/packet-forward-middleware/v3 v3.0.0
+	github.com/strangelove-ventures/packet-forward-middleware/v3 v3.1.5
 	github.com/stretchr/testify v1.8.1
-	github.com/tendermint/tendermint v0.34.22
+	github.com/tendermint/tendermint v0.34.24
 	github.com/tendermint/tm-db v0.6.7
 	google.golang.org/genproto v0.0.0-20221207170731-23e4bf6bdc37
 	google.golang.org/grpc v1.51.0
@@ -28,7 +28,7 @@ require (
 	github.com/99designs/keyring v1.1.6 // indirect
 	github.com/ChainSafe/go-schnorrkel v0.0.0-20200405005733-88cbf1b4c40d // indirect
 	github.com/DataDog/zstd v1.4.5 // indirect
-	github.com/Microsoft/go-winio v0.5.2 // indirect
+	github.com/Microsoft/go-winio v0.6.0 // indirect
 	github.com/Microsoft/hcsshim v0.9.4 // indirect
 	github.com/Workiva/go-datastructures v1.0.53 // indirect
 	github.com/andrew-d/go-termutil v0.0.0-20150726205930-009166a695a2 // indirect
@@ -59,8 +59,8 @@ require (
 	github.com/dgraph-io/badger/v2 v2.2007.2 // indirect
 	github.com/dgraph-io/ristretto v0.0.3 // indirect
 	github.com/dgryski/go-farm v0.0.0-20200201041132-a6ae2369ad13 // indirect
-	github.com/docker/docker v20.10.17+incompatible // indirect
-	github.com/docker/go-units v0.4.0 // indirect
+	github.com/docker/docker v20.10.19+incompatible // indirect
+	github.com/docker/go-units v0.5.0 // indirect
 	github.com/dustin/go-humanize v1.0.1-0.20200219035652-afde56e7acac // indirect
 	github.com/dvsekhvalnov/jose2go v0.0.0-20200901110807-248326c1351b // indirect
 	github.com/emicklei/proto v1.9.0 // indirect
@@ -79,7 +79,7 @@ require (
 	github.com/godbus/dbus v0.0.0-20190726142602-4481cbc300e2 // indirect
 	github.com/gogo/gateway v1.1.0 // indirect
 	github.com/golang/groupcache v0.0.0-20210331224755-41bb18bfe9da // indirect
-	github.com/golang/snappy v0.0.3 // indirect
+	github.com/golang/snappy v0.0.4 // indirect
 	github.com/google/btree v1.0.0 // indirect
 	github.com/google/orderedcode v0.0.1 // indirect
 	github.com/gookit/color v1.5.0 // indirect
@@ -93,6 +93,7 @@ require (
 	github.com/hashicorp/golang-lru v0.5.4 // indirect
 	github.com/hashicorp/hcl v1.0.0 // indirect
 	github.com/hdevalence/ed25519consensus v0.0.0-20210204194344-59a8610d2b87 // indirect
+	github.com/iancoleman/orderedmap v0.2.0 // indirect
 	github.com/iancoleman/strcase v0.2.0 // indirect
 	github.com/imdario/mergo v0.3.12 // indirect
 	github.com/improbable-eng/grpc-web v0.14.1 // indirect
@@ -106,7 +107,7 @@ require (
 	github.com/jpillora/sizestr v1.0.0 // indirect
 	github.com/kevinburke/ssh_config v0.0.0-20190725054713-01f96b0aa0cd // indirect
 	github.com/keybase/go-keychain v0.0.0-20190712205309-48d3d31d256d // indirect
-	github.com/klauspost/compress v1.15.9 // indirect
+	github.com/klauspost/compress v1.15.11 // indirect
 	github.com/lib/pq v1.10.6 // indirect
 	github.com/libp2p/go-buffer-pool v0.1.0 // indirect
 	github.com/magiconair/properties v1.8.6 // indirect
@@ -122,7 +123,7 @@ require (
 	github.com/moby/sys/mountinfo v0.6.0 // indirect
 	github.com/mtibben/percent v0.2.1 // indirect
 	github.com/opencontainers/go-digest v1.0.0 // indirect
-	github.com/opencontainers/image-spec v1.0.3-0.20211202183452-c5a74bcca799 // indirect
+	github.com/opencontainers/image-spec v1.1.0-rc2 // indirect
 	github.com/opencontainers/runc v1.1.3 // indirect
 	github.com/otiai10/copy v1.6.0 // indirect
 	github.com/pelletier/go-toml v1.9.5 // indirect
@@ -133,7 +134,7 @@ require (
 	github.com/prometheus/client_golang v1.12.2 // indirect
 	github.com/prometheus/client_model v0.2.0 // indirect
 	github.com/prometheus/common v0.34.0 // indirect
-	github.com/prometheus/procfs v0.7.3 // indirect
+	github.com/prometheus/procfs v0.8.0 // indirect
 	github.com/radovskyb/watcher v1.0.7 // indirect
 	github.com/rakyll/statik v0.1.7 // indirect
 	github.com/rcrowley/go-metrics v0.0.0-20201227073835-cf1acfcdf475 // indirect
@@ -147,7 +148,7 @@ require (
 	github.com/spf13/jwalterweatherman v1.1.0 // indirect
 	github.com/spf13/viper v1.13.0 // indirect
 	github.com/subosito/gotenv v1.4.1 // indirect
-	github.com/syndtr/goleveldb v1.0.1-0.20200815110645-5c35d600f0ca // indirect
+	github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7 // indirect
 	github.com/takuoki/gocase v1.0.0 // indirect
 	github.com/tendermint/btcd v0.1.1 // indirect
 	github.com/tendermint/crypto v0.0.0-20191022145703-50d29ede1e15 // indirect
@@ -160,16 +161,17 @@ require (
 	github.com/zondax/hid v0.9.0 // indirect
 	go.etcd.io/bbolt v1.3.6 // indirect
 	go.opencensus.io v0.23.0 // indirect
-	golang.org/x/crypto v0.0.0-20220722155217-630584e8d5aa // indirect
+	golang.org/x/crypto v0.1.0 // indirect
 	golang.org/x/exp v0.0.0-20220722155223-a9213eeb770e // indirect
-	golang.org/x/mod v0.6.0-dev.0.20220419223038-86c51ed26bb4 // indirect
-	golang.org/x/net v0.0.0-20221014081412-f15817d10f9b // indirect
-	golang.org/x/sync v0.0.0-20220819030929-7fc1605a5dde // indirect
-	golang.org/x/sys v0.0.0-20220818161305-2296e01440c6 // indirect
-	golang.org/x/term v0.0.0-20220722155259-a9ba230a4035 // indirect
+	golang.org/x/mod v0.6.0 // indirect
+	golang.org/x/net v0.1.0 // indirect
+	golang.org/x/sync v0.0.0-20220929204114-8fcdb60fdcc0 // indirect
+	golang.org/x/sys v0.1.0 // indirect
+	golang.org/x/term v0.1.0 // indirect
 	golang.org/x/text v0.4.0 // indirect
+	golang.org/x/tools v0.2.0 // indirect
 	golang.org/x/xerrors v0.0.0-20220517211312-f3a8303e98df // indirect
-	google.golang.org/protobuf v1.28.1 // indirect
+	google.golang.org/protobuf v1.28.2-0.20220831092852-f930b1dc76e8 // indirect
 	gopkg.in/ini.v1 v1.67.0 // indirect
 	gopkg.in/warnings.v0 v0.1.2 // indirect
 	gopkg.in/yaml.v3 v3.0.1 // indirect
```

### go.sum
```diff
@@ -85,8 +85,8 @@ github.com/Microsoft/go-winio v0.4.16/go.mod h1:XB6nPKklQyQ7GC9LdcBEcBl8PF76WugX
 github.com/Microsoft/go-winio v0.4.17-0.20210211115548-6eac466e5fa3/go.mod h1:JPGBdM1cNvN/6ISo+n8V5iA4v8pBzdOpzfwIujj1a84=
 github.com/Microsoft/go-winio v0.4.17-0.20210324224401-5516f17a5958/go.mod h1:JPGBdM1cNvN/6ISo+n8V5iA4v8pBzdOpzfwIujj1a84=
 github.com/Microsoft/go-winio v0.4.17/go.mod h1:JPGBdM1cNvN/6ISo+n8V5iA4v8pBzdOpzfwIujj1a84=
-github.com/Microsoft/go-winio v0.5.2 h1:a9IhgEQBCUEk6QCdml9CiJGhAws+YwffDHEMp1VMrpA=
-github.com/Microsoft/go-winio v0.5.2/go.mod h1:WpS1mjBmmwHBEWmogvA2mj8546UReBk4v8QkMxJ6pZY=
+github.com/Microsoft/go-winio v0.6.0 h1:slsWYD/zyx7lCXoZVlvQrj0hPTM1HI4+v1sIda2yDvg=
+github.com/Microsoft/go-winio v0.6.0/go.mod h1:cTAf44im0RAYeL23bpB+fzCyDH2MJiz2BO69KH/soAE=
 github.com/Microsoft/hcsshim v0.8.6/go.mod h1:Op3hHsoHPAvb6lceZHDtd9OkTew38wNoXnJs8iY7rUg=
 github.com/Microsoft/hcsshim v0.8.7-0.20190325164909-8abdbb8205e4/go.mod h1:Op3hHsoHPAvb6lceZHDtd9OkTew38wNoXnJs8iY7rUg=
 github.com/Microsoft/hcsshim v0.8.7/go.mod h1:OHd7sQqRFrYd3RmSgbgji+ctCwkbq2wbEYNSzOYtcBQ=
@@ -395,17 +395,18 @@ github.com/docker/distribution v2.7.1-0.20190205005809-0d3efadf0154+incompatible
 github.com/docker/distribution v2.7.1+incompatible/go.mod h1:J2gT2udsDAN96Uj4KfcMRqY0/ypR+oyYUYmja8H+y+w=
 github.com/docker/docker v1.4.2-0.20180625184442-8e610b2b55bf/go.mod h1:eEKB0N0r5NX/I1kEveEz05bcu8tLC/8azJZsviup8Sk=
 github.com/docker/docker v1.4.2-0.20190924003213-a8608b5b67c7/go.mod h1:eEKB0N0r5NX/I1kEveEz05bcu8tLC/8azJZsviup8Sk=
-github.com/docker/docker v20.10.17+incompatible h1:JYCuMrWaVNophQTOrMMoSwudOVEfcegoZZrleKc1xwE=
-github.com/docker/docker v20.10.17+incompatible/go.mod h1:eEKB0N0r5NX/I1kEveEz05bcu8tLC/8azJZsviup8Sk=
+github.com/docker/docker v20.10.19+incompatible h1:lzEmjivyNHFHMNAFLXORMBXyGIhw/UP4DvJwvyKYq64=
+github.com/docker/docker v20.10.19+incompatible/go.mod h1:eEKB0N0r5NX/I1kEveEz05bcu8tLC/8azJZsviup8Sk=
 github.com/docker/docker-credential-helpers v0.6.3/go.mod h1:WRaJzqw3CTB9bk10avuGsjVBZsD05qeibJ1/TYlvc0Y=
 github.com/docker/go-connections v0.4.0 h1:El9xVISelRB7BuFusrZozjnkIM5YnzCViNKohAFqRJQ=
 github.com/docker/go-connections v0.4.0/go.mod h1:Gbd7IOopHjR8Iph03tsViu4nIes5XhDvyHbTtUxmeec=
 github.com/docker/go-events v0.0.0-20170721190031-9461782956ad/go.mod h1:Uw6UezgYA44ePAFQYUehOuCzmy5zmg/+nl2ZfMWGkpA=
 github.com/docker/go-events v0.0.0-20190806004212-e31b211e4f1c/go.mod h1:Uw6UezgYA44ePAFQYUehOuCzmy5zmg/+nl2ZfMWGkpA=
 github.com/docker/go-metrics v0.0.0-20180209012529-399ea8c73916/go.mod h1:/u0gXw0Gay3ceNrsHubL3BtdOL2fHf93USgMTe0W5dI=
 github.com/docker/go-metrics v0.0.1/go.mod h1:cG1hvH2utMXtqgqqYE9plW6lDxS3/5ayHzueweSI3Vw=
-github.com/docker/go-units v0.4.0 h1:3uh0PgVws3nIA0Q+MwDC8yjEPf9zjRfZZWXZYDct3Tw=
 github.com/docker/go-units v0.4.0/go.mod h1:fgPhTUdO+D/Jk86RDLlptpiXQzgHJF7gydDDbaIK4Dk=
+github.com/docker/go-units v0.5.0 h1:69rxXcBk27SvSaaxTtLh/8llcHD8vYHT7WSdRZ/jvr4=
+github.com/docker/go-units v0.5.0/go.mod h1:fgPhTUdO+D/Jk86RDLlptpiXQzgHJF7gydDDbaIK4Dk=
 github.com/docker/libtrust v0.0.0-20150114040149-fa567046d9b1/go.mod h1:cyGadeNEkKy96OOhEzfZl+yxihPEzKnqJwvfuSUqbZE=
 github.com/docker/spdystream v0.0.0-20160310174837-449fdfce4d96/go.mod h1:Qh8CwZgvJUkLughtfhJv5dyTYa91l1fOUCrgjqmcifM=
 github.com/docopt/docopt-go v0.0.0-20180111231733-ee0de3bc6815/go.mod h1:WwZ+bS3ebgob9U8Nd0kOddGdZWjyMGR8Wziv+TBNwSE=
@@ -577,8 +578,8 @@ github.com/golang/protobuf v1.5.2/go.mod h1:XVQd3VNwM+JqD3oG2Ue2ip4fOMUkwXdXDdiu
 github.com/golang/snappy v0.0.0-20180518054509-2e65f85255db/go.mod h1:/XxbfmMg8lxefKM7IXC3fBNl/7bRcc72aCRzEWrmP2Q=
 github.com/golang/snappy v0.0.1/go.mod h1:/XxbfmMg8lxefKM7IXC3fBNl/7bRcc72aCRzEWrmP2Q=
 github.com/golang/snappy v0.0.3-0.20201103224600-674baa8c7fc3/go.mod h1:/XxbfmMg8lxefKM7IXC3fBNl/7bRcc72aCRzEWrmP2Q=
-github.com/golang/snappy v0.0.3 h1:fHPg5GQYlCeLIPB9BZqMVR5nR9A+IM5zcgeTdjMYmLA=
-github.com/golang/snappy v0.0.3/go.mod h1:/XxbfmMg8lxefKM7IXC3fBNl/7bRcc72aCRzEWrmP2Q=
+github.com/golang/snappy v0.0.4 h1:yAGX7huGHXlcLOEtBnF4w7FQwA26wojNCwOYAEhLjQM=
+github.com/golang/snappy v0.0.4/go.mod h1:/XxbfmMg8lxefKM7IXC3fBNl/7bRcc72aCRzEWrmP2Q=
 github.com/google/btree v0.0.0-20180813153112-4030bb1f1f0c/go.mod h1:lNA+9X1NB3Zf8V7Ke586lFgjr2dZNuvo3lPJSGZ5JPQ=
 github.com/google/btree v1.0.0 h1:0udJVsspx3VBr5FwtLhQQtuAsVc79tTq0ocGIPAU6qo=
 github.com/google/btree v1.0.0/go.mod h1:lNA+9X1NB3Zf8V7Ke586lFgjr2dZNuvo3lPJSGZ5JPQ=
@@ -702,6 +703,8 @@ github.com/hpcloud/tail v1.0.0/go.mod h1:ab1qPbhIpdTxEkNHXyeSf5vhxWSCs/tWer42PpO
 github.com/hudl/fargo v1.3.0/go.mod h1:y3CKSmjA+wD2gak7sUSXTAoopbhU08POFhmITJgmKTg=
 github.com/huin/goupnp v1.0.0/go.mod h1:n9v9KO1tAxYH82qOn+UTIFQDmx5n1Zxd/ClZDMX7Bnc=
 github.com/huin/goutil v0.0.0-20170803182201-1ca381bf3150/go.mod h1:PpLOETDnJ0o3iZrZfqZzyLl6l7F3c6L1oWn7OICBi6o=
+github.com/iancoleman/orderedmap v0.2.0 h1:sq1N/TFpYH++aViPcaKjys3bDClUEU7s5B+z6jq8pNA=
+github.com/iancoleman/orderedmap v0.2.0/go.mod h1:N0Wam8K1arqPXNWjMo21EXnBPOPp36vB07FNRdD2geA=
 github.com/iancoleman/strcase v0.2.0 h1:05I4QRnGpI0m37iZQRuskXh+w77mr6Z41lwQzuHLwW0=
 github.com/iancoleman/strcase v0.2.0/go.mod h1:iwCmte+B7n89clKwxIoIXy/HfoL7AsD47ZCWhYzw7ho=
 github.com/ianlancetaylor/demangle v0.0.0-20181102032728-5e5cf60278f6/go.mod h1:aSSvb/t6k1mPoxDqO4vJh6VOCGPwU4O0C2/Eqndh1Sc=
@@ -772,8 +775,8 @@ github.com/klauspost/compress v1.10.3/go.mod h1:aoV0uJVorq1K+umq18yTdKaF57EivdYs
 github.com/klauspost/compress v1.11.3/go.mod h1:aoV0uJVorq1K+umq18yTdKaF57EivdYsUV+/s2qKfXs=
 github.com/klauspost/compress v1.11.7/go.mod h1:aoV0uJVorq1K+umq18yTdKaF57EivdYsUV+/s2qKfXs=
 github.com/klauspost/compress v1.11.13/go.mod h1:aoV0uJVorq1K+umq18yTdKaF57EivdYsUV+/s2qKfXs=
-github.com/klauspost/compress v1.15.9 h1:wKRjX6JRtDdrE9qwa4b/Cip7ACOshUI4smpCQanqjSY=
-github.com/klauspost/compress v1.15.9/go.mod h1:PhcZ0MbTNciWF3rruxRgKxI5NkcHHrHUDtV4Yw2GlzU=
+github.com/klauspost/compress v1.15.11 h1:Lcadnb3RKGin4FYM/orgq0qde+nc15E5Cbqg4B9Sx9c=
+github.com/klauspost/compress v1.15.11/go.mod h1:QPwzmACJjUTFsnSHH934V6woptycfrDDJnH7hvFVbGM=
 github.com/konsorten/go-windows-terminal-sequences v1.0.1/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
 github.com/konsorten/go-windows-terminal-sequences v1.0.2/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
 github.com/konsorten/go-windows-terminal-sequences v1.0.3/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
@@ -936,8 +939,8 @@ github.com/opencontainers/go-digest v1.0.0 h1:apOUWs51W5PlhuyGyz9FCeeBIOUDA/6nW8
 github.com/opencontainers/go-digest v1.0.0/go.mod h1:0JzlMkj0TRzQZfJkVvzbP0HBR3IKzErnv2BNG4W4MAM=
 github.com/opencontainers/image-spec v1.0.0/go.mod h1:BtxoFyWECRxE4U/7sNtV5W15zMzWCbyJoFRP3s7yZA0=
 github.com/opencontainers/image-spec v1.0.1/go.mod h1:BtxoFyWECRxE4U/7sNtV5W15zMzWCbyJoFRP3s7yZA0=
-github.com/opencontainers/image-spec v1.0.3-0.20211202183452-c5a74bcca799 h1:rc3tiVYb5z54aKaDfakKn0dDjIyPpTtszkjuMzyt7ec=
-github.com/opencontainers/image-spec v1.0.3-0.20211202183452-c5a74bcca799/go.mod h1:BtxoFyWECRxE4U/7sNtV5W15zMzWCbyJoFRP3s7yZA0=
+github.com/opencontainers/image-spec v1.1.0-rc2 h1:2zx/Stx4Wc5pIPDvIxHXvXtQFW/7XWJGmnM7r3wg034=
+github.com/opencontainers/image-spec v1.1.0-rc2/go.mod h1:3OVijpioIKYWTqjiG0zfF6wvoJ4fAXGbjdZuI2NgsRQ=
 github.com/opencontainers/runc v0.0.0-20190115041553-12f6a991201f/go.mod h1:qT5XzbpPznkRYVz/mWwUaVBUv2rmF59PVA73FjuZG0U=
 github.com/opencontainers/runc v0.1.1/go.mod h1:qT5XzbpPznkRYVz/mWwUaVBUv2rmF59PVA73FjuZG0U=
 github.com/opencontainers/runc v1.0.0-rc8.0.20190926000215-3e425f80a8c9/go.mod h1:qT5XzbpPznkRYVz/mWwUaVBUv2rmF59PVA73FjuZG0U=
@@ -1052,8 +1055,9 @@ github.com/prometheus/procfs v0.1.3/go.mod h1:lV6e/gmhEcM9IjHGsFOCxxuZ+z1YqCvr4O
 github.com/prometheus/procfs v0.2.0/go.mod h1:lV6e/gmhEcM9IjHGsFOCxxuZ+z1YqCvr4OA4YeYWdaU=
 github.com/prometheus/procfs v0.3.0/go.mod h1:lV6e/gmhEcM9IjHGsFOCxxuZ+z1YqCvr4OA4YeYWdaU=
 github.com/prometheus/procfs v0.6.0/go.mod h1:cz+aTbrPOrUb4q7XlbU9ygM+/jj0fzG6c1xBZuNvfVA=
-github.com/prometheus/procfs v0.7.3 h1:4jVXhlkAyzOScmCkXBTOLRLTz8EeU+eyjrwB/EPq0VU=
 github.com/prometheus/procfs v0.7.3/go.mod h1:cz+aTbrPOrUb4q7XlbU9ygM+/jj0fzG6c1xBZuNvfVA=
+github.com/prometheus/procfs v0.8.0 h1:ODq8ZFEaYeCaZOJlZZdJA2AbQR98dSHSM1KW/You5mo=
+github.com/prometheus/procfs v0.8.0/go.mod h1:z7EfXMXOkbkqb9IINtpCn86r/to3BnA0uaxHdg830/4=
 github.com/prometheus/tsdb v0.6.2-0.20190402121629-4f204dcbc150/go.mod h1:qhTCs0VvXwvX/y3TZrWD7rabWM+ijKTux40TwIPHuXU=
 github.com/prometheus/tsdb v0.7.1/go.mod h1:qhTCs0VvXwvX/y3TZrWD7rabWM+ijKTux40TwIPHuXU=
 github.com/radovskyb/watcher v1.0.7 h1:AYePLih6dpmS32vlHfhCeli8127LzkIgwJGcwwe8tUE=
@@ -1127,8 +1131,8 @@ github.com/spf13/cobra v0.0.2-0.20171109065643-2da4a54c5cee/go.mod h1:1l0Ry5zgKv
 github.com/spf13/cobra v0.0.3/go.mod h1:1l0Ry5zgKvJasoi3XT1TypsSe7PqH0Sj9dhYf7v3XqQ=
 github.com/spf13/cobra v0.0.5/go.mod h1:3K3wKZymM7VvHMDS9+Akkh4K60UwM26emMESw8tLCHU=
 github.com/spf13/cobra v1.0.0/go.mod h1:/6GTrnGXV9HjY+aR4k0oJ5tcvakLuG6EuKReYlHNrgE=
-github.com/spf13/cobra v1.5.0 h1:X+jTBEBqF0bHN+9cSMgmfuvv2VHJ9ezmFNf9Y/XstYU=
-github.com/spf13/cobra v1.5.0/go.mod h1:dWXEIy2H428czQCjInthrTRUg7yKbok+2Qi/yBIJoUM=
+github.com/spf13/cobra v1.6.1 h1:o94oiPyS4KD1mPy2fmcYYHHfCxLqYjJOhGsCHFZtEzA=
+github.com/spf13/cobra v1.6.1/go.mod h1:IOw/AERYS7UzyrGinqmz6HLUo219MORXGxhbaJUqzrY=
 github.com/spf13/jwalterweatherman v1.0.0/go.mod h1:cQK4TGJAtQXfYWX+Ddv3mKDzgVb68N+wFjFa4jdeBTo=
 github.com/spf13/jwalterweatherman v1.1.0 h1:ue6voC5bR5F8YxI5S67j9i582FU4Qvo2bmqnqMYADFk=
 github.com/spf13/jwalterweatherman v1.1.0/go.mod h1:aNWZUN0dPAAO/Ljvb5BEdw96iTZ0EXowPYD95IqWIGo=
@@ -1146,8 +1150,8 @@ github.com/status-im/keycard-go v0.0.0-20190316090335-8537d3370df4/go.mod h1:RZL
 github.com/steakknife/bloomfilter v0.0.0-20180922174646-6819c0d2a570/go.mod h1:8OR4w3TdeIHIh1g6EMY5p0gVNOovcWC+1vpc7naMuAw=
 github.com/steakknife/hamming v0.0.0-20180906055917-c99c65617cd3/go.mod h1:hpGUWaI9xL8pRQCTXQgocU38Qw1g0Us7n5PxxTwTCYU=
 github.com/stefanberger/go-pkcs11uri v0.0.0-20201008174630-78d3cae3a980/go.mod h1:AO3tvPzVZ/ayst6UlUKUv6rcPQInYe3IknH3jYhAKu8=
-github.com/strangelove-ventures/packet-forward-middleware/v3 v3.0.0 h1:V1RVRa2hga4TV//RQpk2PCt314slS3N12024TsJoJUo=
-github.com/strangelove-ventures/packet-forward-middleware/v3 v3.0.0/go.mod h1:sRBHb6KwuHQVc07vy8Ice9wUKVdvzn7eEms9scr2Zco=
+github.com/strangelove-ventures/packet-forward-middleware/v3 v3.1.5 h1:iXXjziCSAebzuRUPFSnqD7epSDB8LEPgkh9zhbj7ha4=
+github.com/strangelove-ventures/packet-forward-middleware/v3 v3.1.5/go.mod h1:ncgsf5rykh36HkM16BNcKKx1XzVRdWXt+4pph1syDHE=
 github.com/streadway/amqp v0.0.0-20190404075320-75d898a42a94/go.mod h1:AZpEONHx3DKn8O/DFsRAY58/XVQiIPMTMB1SddzLXVw=
 github.com/streadway/amqp v0.0.0-20190827072141-edfb9018d271/go.mod h1:AZpEONHx3DKn8O/DFsRAY58/XVQiIPMTMB1SddzLXVw=
 github.com/streadway/handy v0.0.0-20190108123426-d5acb3125c2a/go.mod h1:qNTQ5P5JnDBl6z3cMAg/SywNDC5ABu5ApDIw6lUbRmI=
@@ -1174,8 +1178,9 @@ github.com/subosito/gotenv v1.4.1/go.mod h1:ayKnFf/c6rvx/2iiLrJUk1e6plDbT3edrFNG
 github.com/syndtr/gocapability v0.0.0-20170704070218-db04d3cc01c8/go.mod h1:hkRG7XYTFWNJGYcbNJQlaLq0fg1yr4J4t/NcTQtrfww=
 github.com/syndtr/gocapability v0.0.0-20180916011248-d98352740cb2/go.mod h1:hkRG7XYTFWNJGYcbNJQlaLq0fg1yr4J4t/NcTQtrfww=
 github.com/syndtr/gocapability v0.0.0-20200815063812-42c35b437635/go.mod h1:hkRG7XYTFWNJGYcbNJQlaLq0fg1yr4J4t/NcTQtrfww=
-github.com/syndtr/goleveldb v1.0.1-0.20200815110645-5c35d600f0ca h1:Ld/zXl5t4+D69SiV4JoN7kkfvJdOWlPpfxrzxpLMoUk=
 github.com/syndtr/goleveldb v1.0.1-0.20200815110645-5c35d600f0ca/go.mod h1:u2MKkTVTVJWe5D1rCvame8WqhBd88EuIwODJZ1VHCPM=
+github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7 h1:epCh84lMvA70Z7CTTCmYQn2CKbY8j86K7/FAIr141uY=
+github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7/go.mod h1:q4W45IWZaF22tdD+VEXcAWRA037jwmWEB5VWYORlTpc=
 github.com/takuoki/gocase v1.0.0 h1:gPwLJTWVm2T1kUiCsKirg/faaIUGVTI0FA3SYr75a44=
 github.com/takuoki/gocase v1.0.0/go.mod h1:QgOKJrbuJoDrtoKswBX1/Dw8mJrkOV9tbQZJaxaJ6zc=
 github.com/tchap/go-patricia v2.2.6+incompatible/go.mod h1:bmLyhP68RS6kStMGxByiQ23RP/odRBOTVjwp2cDyi6I=
@@ -1189,8 +1194,8 @@ github.com/tendermint/go-amino v0.16.0 h1:GyhmgQKvqF82e2oZeuMSp9JTN0N09emoSZlb2l
 github.com/tendermint/go-amino v0.16.0/go.mod h1:TQU0M1i/ImAo+tYpZi73AU3V/dKeCoMC9Sphe2ZwGME=
 github.com/tendermint/spn v0.2.1-0.20220708132853-26a17f03c072 h1:J7+gbosE+lUg/m6wGNHs8xRM5ugU3FbdLWwaNg5b9kw=
 github.com/tendermint/spn v0.2.1-0.20220708132853-26a17f03c072/go.mod h1:Ek8O0rqggK/yz1ya55hr0tVUPvsAR5sHLLLClTbuPrc=
-github.com/tendermint/tendermint v0.34.22 h1:XMhtC8s8QqJO4l/dn+TkQvevTRSow3Vixjclr41o+2Q=
-github.com/tendermint/tendermint v0.34.22/go.mod h1:YpP5vBEAKUT4g6oyfjKgFeZmdB/GjkJAxfF+cgmJg6Y=
+github.com/tendermint/tendermint v0.34.24 h1:879MKKJWYYPJEMMKME+DWUTY4V9f/FBpnZDI82ky+4k=
+github.com/tendermint/tendermint v0.34.24/go.mod h1:rXVrl4OYzmIa1I91av3iLv2HS0fGSiucyW9J4aMTpKI=
 github.com/tendermint/tm-db v0.6.7 h1:fE00Cbl0jayAoqlExN6oyQJ7fR/ZtoVOmvPJ//+shu8=
 github.com/tendermint/tm-db v0.6.7/go.mod h1:byQDzFkZV1syXr/ReXS808NxA2xvyuuVgXOJ/088L6I=
 github.com/tidwall/gjson v1.6.7/go.mod h1:zeFuBCIqD4sN/gmqBzZ4j7Jd6UcA2Fc56x7QFsv+8fI=
@@ -1301,8 +1306,8 @@ golang.org/x/crypto v0.0.0-20210322153248-0c34fe9e7dc2/go.mod h1:T9bdIzuCu7OtxOm
 golang.org/x/crypto v0.0.0-20210421170649-83a5a9bb288b/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
 golang.org/x/crypto v0.0.0-20210616213533-5ff15b29337e/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
 golang.org/x/crypto v0.0.0-20211108221036-ceb1ce70b4fa/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
-golang.org/x/crypto v0.0.0-20220722155217-630584e8d5aa h1:zuSxTR4o9y82ebqCUJYNGJbGPo6sKVl54f/TVDObg1c=
-golang.org/x/crypto v0.0.0-20220722155217-630584e8d5aa/go.mod h1:IxCIyHEi3zRg3s0A5j5BB6A9Jmi73HwBIUl50j+osU4=
+golang.org/x/crypto v0.1.0 h1:MDRAIl0xIo9Io2xV565hzXHw3zVseKrJKodhohM5CjU=
+golang.org/x/crypto v0.1.0/go.mod h1:RecgLatLF4+eUMCP1PoPZQb+cVrJcOPbHkTkbkB9sbw=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190306152737-a1d7652674e8/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190510132918-efd6b22b2522/go.mod h1:ZjyILWgesfNpC6sMxTJOJm9Kp84zZh5NQWvqDGG3Qr8=
@@ -1342,8 +1347,8 @@ golang.org/x/mod v0.3.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.1/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.2/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
-golang.org/x/mod v0.6.0-dev.0.20220419223038-86c51ed26bb4 h1:6zppjxzCulZykYSLyVDYbneBfbaBIQPYMevg0bEwv2s=
-golang.org/x/mod v0.6.0-dev.0.20220419223038-86c51ed26bb4/go.mod h1:jJ57K6gSWd91VN4djpZkiMVwK6gcyfeH4XE8wZrZaV4=
+golang.org/x/mod v0.6.0 h1:b9gGHsz9/HhJ3HF5DHQytPpuwocVTChQJK3AvoLRD5I=
+golang.org/x/mod v0.6.0/go.mod h1:4mET923SAdbXp2ki8ey+zGs1SLqsuM2Y0uvdZR/fUNI=
 golang.org/x/net v0.0.0-20180719180050-a680a1efc54d/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180724234803-3673e40ba225/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180906233101-161cd47e91fd/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
@@ -1400,8 +1405,8 @@ golang.org/x/net v0.0.0-20210614182718-04defd469f4e/go.mod h1:9nx3DQGgdP8bBQD5qx
 golang.org/x/net v0.0.0-20210825183410-e898025ed96a/go.mod h1:9nx3DQGgdP8bBQD5qxJ1jj9UTztislL4KSBs9R2vV5Y=
 golang.org/x/net v0.0.0-20220127200216-cd36cc0744dd/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
-golang.org/x/net v0.0.0-20221014081412-f15817d10f9b h1:tvrvnPFcdzp294diPnrdZZZ8XUt2Tyj7svb7X52iDuU=
-golang.org/x/net v0.0.0-20221014081412-f15817d10f9b/go.mod h1:YDH+HFinaLZZlnHAfSS6ZXJJ9M9t4Dl22yv3iI2vPwk=
+golang.org/x/net v0.1.0 h1:hZ/3BUoy5aId7sCpA/Tc5lt8DkFgdVS2onTpJsZ/fl0=
+golang.org/x/net v0.1.0/go.mod h1:Cx3nUiGt4eDBEyega/BKRp+/AlGL8hYe7U9odMt2Cco=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
 golang.org/x/oauth2 v0.0.0-20190226205417-e64efc72b421/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
 golang.org/x/oauth2 v0.0.0-20190604053449-0f29369cfe45/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
@@ -1424,8 +1429,8 @@ golang.org/x/sync v0.0.0-20200625203802-6e8e738ad208/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20201207232520-09787c993a3a/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
-golang.org/x/sync v0.0.0-20220819030929-7fc1605a5dde h1:ejfdSekXMDxDLbRrJMwUk6KnSLZ2McaUCVcIKM+N6jc=
-golang.org/x/sync v0.0.0-20220819030929-7fc1605a5dde/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
+golang.org/x/sync v0.0.0-20220929204114-8fcdb60fdcc0 h1:cu5kTvlzcw1Q5S9f5ip1/cpiB4nXvw1XYzFPGgzLUOY=
+golang.org/x/sync v0.0.0-20220929204114-8fcdb60fdcc0/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sys v0.0.0-20180823144017-11551d06cbcc/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180905080454-ebe1bf3edb33/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180909124046-d0be0721c37e/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -1527,13 +1532,13 @@ golang.org/x/sys v0.0.0-20220114195835-da31bd327af9/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20220412211240-33da011f77ad/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220715151400-c0bba94af5f8/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220811171246-fbc7d0a398ab/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/sys v0.0.0-20220818161305-2296e01440c6 h1:Sx/u41w+OwrInGdEckYmEuU5gHoGSL4QbDz3S9s6j4U=
-golang.org/x/sys v0.0.0-20220818161305-2296e01440c6/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.1.0 h1:kunALQeHf1/185U1i0GOB/fy1IPRDDpuoOOqRReG57U=
+golang.org/x/sys v0.1.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210615171337-6886f2dfbf5b/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
-golang.org/x/term v0.0.0-20220722155259-a9ba230a4035 h1:Q5284mrmYTpACcm+eAKjKJH48BBwSyfJqmmGDTtT8Vc=
-golang.org/x/term v0.0.0-20220722155259-a9ba230a4035/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
+golang.org/x/term v0.1.0 h1:g6Z6vPFA9dYBAF7DWcH6sCcOntplXsDKcliusYijMlw=
+golang.org/x/term v0.1.0/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.1-0.20180807135948-17ff2d5776d2/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
@@ -1614,6 +1619,8 @@ golang.org/x/tools v0.0.0-20210108195828-e2f9c7f1fc8e/go.mod h1:emZCQorbCU4vsT4f
 golang.org/x/tools v0.1.0/go.mod h1:xkSsbof2nBLbhDlRMhhhyNLN/zl3eTqcnHD5viDpcZ0=
 golang.org/x/tools v0.1.1/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
 golang.org/x/tools v0.1.5/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
+golang.org/x/tools v0.2.0 h1:G6AHpWxTMGY1KyEYoAQ5WTtIekUUvDNjan3ugu60JvE=
+golang.org/x/tools v0.2.0/go.mod h1:y4OqIKeOV/fWJetJ8bXPU1sEVniLMIyDAZWeHdV+NTA=
 golang.org/x/xerrors v0.0.0-20190717185122-a985d3407aa7/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191011141410-1b5146add898/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191204190536-9bdfabe68543/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
@@ -1712,8 +1719,8 @@ google.golang.org/protobuf v1.25.0/go.mod h1:9JNX74DMeImyA3h4bdi1ymwjUzf21/xIlba
 google.golang.org/protobuf v1.26.0-rc.1/go.mod h1:jlhhOSvTdKEhbULTjvd4ARK9grFBp09yW+WbY/TyQbw=
 google.golang.org/protobuf v1.26.0/go.mod h1:9q0QmTI4eRPtz6boOQmLYwt+qCgq0jsYwAQnmE0givc=
 google.golang.org/protobuf v1.27.1/go.mod h1:9q0QmTI4eRPtz6boOQmLYwt+qCgq0jsYwAQnmE0givc=
-google.golang.org/protobuf v1.28.1 h1:d0NfwRgPtno5B1Wa6L2DAG+KivqkdutMf1UhdNx175w=
-google.golang.org/protobuf v1.28.1/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
+google.golang.org/protobuf v1.28.2-0.20220831092852-f930b1dc76e8 h1:KR8+MyP7/qOlV+8Af01LtjL04bu7on42eVsxT4EyBQk=
+google.golang.org/protobuf v1.28.2-0.20220831092852-f930b1dc76e8/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
 gopkg.in/airbrake/gobrake.v2 v2.0.9/go.mod h1:/h5ZAUhDkGaJfjzjKLSjv6zCL6O0LLBxU4K+aSYdM/U=
 gopkg.in/alecthomas/kingpin.v2 v2.2.6/go.mod h1:FMv+mEhP44yOT+4EoQTLFTRgOQ1FBLkstjWtayDeSgw=
 gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
```

### testing/irc_test.go
```diff
@@ -8,7 +8,7 @@ import (
 	"github.com/stretchr/testify/suite"
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
-	"github.com/strangelove-ventures/packet-forward-middleware/v3/router/keeper"
+	routertypes "github.com/strangelove-ventures/packet-forward-middleware/v3/router/types"
 
 	"encoding/json"
 )
@@ -118,7 +118,8 @@ func (suite *IrcTestSuite) TestHandleMsgMiddlewareTransfer() {
 	rollapp1bds := &suite.rollapp1.TestChainClient.(*DymintTestChainClient).bds
 	rollapp2bds := &suite.rollapp2.TestChainClient.(*DymintTestChainClient).bds
 
-	amount, ok := sdk.NewIntFromString("1000")
+	// This value used to cause panic in the forward middleware and fail the test
+	amount, ok := sdk.NewIntFromString("9900000000000000000")
 	suite.Require().True(ok)
 
 	//************************************************************************
@@ -133,8 +134,8 @@ func (suite *IrcTestSuite) TestHandleMsgMiddlewareTransfer() {
 		suite.rollapp1.SenderAccount.GetAddress().String(),
 		suite.hubChain.SenderAccount.GetAddress().String(),
 		timeoutHeight, 0)
-	nextMetadata := &keeper.PacketMetadata{
-		Forward: &keeper.ForwardMetadata{
+	nextMetadata := &routertypes.PacketMetadata{
+		Forward: &routertypes.ForwardMetadata{
 			Receiver: suite.rollapp2.SenderAccount.GetAddress().String(),
 			Port:     pathRollapp2toHub.EndpointB.ChannelConfig.PortID,
 			Channel:  pathRollapp2toHub.EndpointB.ChannelID,
@@ -225,8 +226,8 @@ func (suite *IrcTestSuite) TestHandleMsgMiddlewareTransfer() {
 		suite.rollapp2.SenderAccount.GetAddress().String(),
 		suite.hubChain.SenderAccount.GetAddress().String(),
 		timeoutHeight, 0)
-	nextMetadata = &keeper.PacketMetadata{
-		Forward: &keeper.ForwardMetadata{
+	nextMetadata = &routertypes.PacketMetadata{
+		Forward: &routertypes.ForwardMetadata{
 			Receiver: suite.rollapp1.SenderAccount.GetAddress().String(),
 			Port:     pathRollapp1toHub.EndpointB.ChannelConfig.PortID,
 			Channel:  pathRollapp1toHub.EndpointB.ChannelID,
```
