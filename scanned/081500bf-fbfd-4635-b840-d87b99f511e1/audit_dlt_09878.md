# [?] security: upgrade critical dependencies to fix vulnerabilities (#4779)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2026-03-05
Source: https://github.com/iotexproject/iotex-core/commit/504a27f5f548e777b2c4f1915bd387c5eddaeb70
Type: security-commit

## Details
security: upgrade critical dependencies to fix vulnerabilities (#4779)

Co-authored-by: Raullen <raullenstudio@Raullens-Mac-Studio.local>
Co-authored-by: envestcc <chen1233216@hotmail.com>

## Patch
### Dockerfile
```diff
@@ -1,4 +1,4 @@
-FROM golang:1.23.0-alpine AS build
+FROM golang:1.24-alpine AS build
 
 WORKDIR /go/apps/iotex-core
 
```

### api/coreservice.go
```diff
@@ -1859,7 +1859,7 @@ func (core *coreService) estimateExecutionGasConsumptionAt(ctx context.Context,
 	if !enough {
 		if receipt.Status == uint64(iotextypes.ReceiptStatus_ErrExecutionReverted) {
 			if len(receipt.ExecutionRevertMsg()) > 0 {
-				return 0, retval, status.Errorf(codes.InvalidArgument, fmt.Sprintf("execution simulation is reverted due to the reason: %s", receipt.ExecutionRevertMsg()))
+				return 0, retval, status.Errorf(codes.InvalidArgument, "execution simulation is reverted due to the reason: %s", receipt.ExecutionRevertMsg())
 			}
 			return 0, retval, status.Error(codes.InvalidArgument, "execution reverted")
 		}
```

### db/trie/kvstoreimpl.go
```diff
@@ -136,7 +136,7 @@ func (s *kvStoreImpl) Get(key []byte) ([]byte, error) {
 	_trieKeystoreMtc.WithLabelValues("get").Inc()
 	value, err := s.dao.Get(s.bucket, key)
 	if errors.Cause(err) == db.ErrNotExist {
-		return nil, errors.Wrapf(ErrNotExist, err.Error())
+		return nil, errors.Wrap(ErrNotExist, err.Error())
 	}
 
 	return value, err
```

### go.mod
```diff
@@ -1,8 +1,6 @@
 module github.com/iotexproject/iotex-core/v2
 
-go 1.23.0
-
-toolchain go1.23.7
+go 1.24.6
 
 require (
 	dario.cat/mergo v1.0.2
@@ -35,20 +33,20 @@ require (
 	github.com/iotexproject/iotex-election v0.3.8-0.20251015031218-8df952babca1
 	github.com/iotexproject/iotex-proto v0.6.6-0.20260211020747-f26bd969ed16
 	github.com/ipfs/go-ipfs-api v0.7.0
-	github.com/libp2p/go-libp2p v0.39.0
+	github.com/libp2p/go-libp2p v0.46.0
 	github.com/libp2p/go-libp2p-pubsub v0.13.0
 	github.com/mackerelio/go-osstat v0.2.4
 	github.com/minio/blake2b-simd v0.0.0-20160723061019-3f5f724cb5b1
 	github.com/mohae/deepcopy v0.0.0-20170929034955-c48cc78d4826
-	github.com/multiformats/go-multiaddr v0.14.0
+	github.com/multiformats/go-multiaddr v0.16.0
 	github.com/pkg/errors v0.9.1
-	github.com/prometheus/client_golang v1.20.5
-	github.com/prometheus/client_model v0.6.1
+	github.com/prometheus/client_golang v1.22.0
+	github.com/prometheus/client_model v0.6.2
 	github.com/rodaine/table v1.0.1
 	github.com/schollz/progressbar/v2 v2.15.0
 	github.com/shirou/gopsutil/v3 v3.24.3
 	github.com/spf13/cobra v1.8.1
-	github.com/stretchr/testify v1.10.0
+	github.com/stretchr/testify v1.11.1
 	github.com/tidwall/gjson v1.11.0
 	github.com/tyler-smith/go-bip39 v1.1.0
 	github.com/uptrace/opentelemetry-go-extra/otelzap v0.2.2
@@ -65,14 +63,14 @@ require (
 	go.uber.org/config v1.3.1
 	go.uber.org/mock v0.5.2
 	go.uber.org/zap v1.27.0
-	golang.org/x/crypto v0.36.0
-	golang.org/x/net v0.37.0
-	golang.org/x/sync v0.12.0
-	golang.org/x/text v0.23.0
-	golang.org/x/time v0.9.0
+	golang.org/x/crypto v0.44.0
+	golang.org/x/net v0.47.0
+	golang.org/x/sync v0.18.0
+	golang.org/x/text v0.31.0
+	golang.org/x/time v0.12.0
 	google.golang.org/genproto v0.0.0-20230410155749-daa745c078e1
 	google.golang.org/grpc v1.69.4
-	google.golang.org/protobuf v1.36.4
+	google.golang.org/protobuf v1.36.6
 	gopkg.in/yaml.v2 v2.4.0
 )
 
@@ -87,14 +85,14 @@ require (
 	github.com/anacrolix/dht/v2 v2.21.1 // indirect
 	github.com/anacrolix/envpprof v1.3.0 // indirect
 	github.com/anacrolix/generics v0.0.0-20230816105729-c755655aee45 // indirect
-	github.com/anacrolix/go-libutp v1.3.1 // indirect
+	github.com/anacrolix/go-libutp v1.3.2 // indirect
 	github.com/anacrolix/log v0.15.2 // indirect
 	github.com/anacrolix/missinggo v1.3.0 // indirect
 	github.com/anacrolix/missinggo/perf v1.0.0 // indirect
-	github.com/anacrolix/missinggo/v2 v2.7.2-0.20230527121029-a582b4f397b9 // indirect
-	github.com/anacrolix/mmsg v1.0.0 // indirect
+	github.com/anacrolix/missinggo/v2 v2.10.0 // indirect
+	github.com/anacrolix/mmsg v1.0.1 // indirect
 	github.com/anacrolix/multiless v0.3.1-0.20221221005021-2d12701f83f7 // indirect
-	github.com/anacrolix/stm v0.4.1-0.20221221005312-96d17df0e496 // indirect
+	github.com/anacrolix/stm v0.5.0 // indirect
 	github.com/anacrolix/sync v0.5.1 // indirect
 	github.com/anacrolix/torrent v1.52.6-0.20231201115409-7ea994b6bbd8 // indirect
 	github.com/anacrolix/upnp v0.1.3-0.20220123035249-922794e51c96 // indirect
@@ -115,9 +113,7 @@ require (
 	github.com/cockroachdb/logtags v0.0.0-20230118201751-21c54148d20b // indirect
 	github.com/cockroachdb/redact v1.1.5 // indirect
 	github.com/cockroachdb/tokenbucket v0.0.0-20230807174530-cc333fc44b06 // indirect
-	github.com/consensys/bavard v0.1.27 // indirect
-	github.com/consensys/gnark-crypto v0.16.0 // indirect
-	github.com/containerd/cgroups v1.1.0 // indirect
+	github.com/consensys/gnark-crypto v0.18.1 // indirect
 	github.com/containerd/cgroups/v3 v3.0.3 // indirect
 	github.com/coreos/go-systemd/v22 v22.5.0 // indirect
 	github.com/crackcomm/go-gitignore v0.0.0-20241020182519-7843d2ba8fdf // indirect
@@ -128,12 +124,11 @@ require (
 	github.com/davidlazar/go-crypto v0.0.0-20200604182044-b73af7476f6c // indirect
 	github.com/deckarep/golang-set v1.8.0 // indirect
 	github.com/deckarep/golang-set/v2 v2.6.0 // indirect
-	github.com/decred/dcrd/dcrec/secp256k1/v4 v4.3.0 // indirect
+	github.com/decred/dcrd/dcrec/secp256k1/v4 v4.4.0 // indirect
 	github.com/dlclark/regexp2 v1.7.0 // indirect
 	github.com/dop251/goja v0.0.0-20230806174421-c933cf95e127 // indirect
 	github.com/dustin/go-humanize v1.0.1 // indirect
 	github.com/edsrzf/mmap-go v1.1.0 // indirect
-	github.com/elastic/gosigar v0.14.3 // indirect
 	github.com/emicklei/dot v1.6.1 // indirect
 	github.com/erigontech/erigon-snapshot v1.3.0 // indirect
 	github.com/erigontech/mdbx-go v0.27.24 // indirect
@@ -150,11 +145,10 @@ require (
 	github.com/go-llsqlite/crawshaw v0.4.0 // indirect
 	github.com/go-sourcemap/sourcemap v2.1.3+incompatible // indirect
 	github.com/go-stack/stack v1.8.1 // indirect
-	github.com/go-task/slim-sprig/v3 v3.0.0 // indirect
 	github.com/goccy/go-json v0.10.4 // indirect
 	github.com/godbus/dbus/v5 v5.1.0 // indirect
 	github.com/gofrs/flock v0.8.1 // indirect
-	github.com/golang-jwt/jwt/v4 v4.5.1 // indirect
+	github.com/golang-jwt/jwt/v4 v4.5.2 // indirect
 	github.com/golang/mock v1.6.0 // indirect
 	github.com/golang/protobuf v1.5.4 // indirect
 	github.com/google/btree v1.1.2 // indirect
@@ -178,27 +172,25 @@ require (
 	github.com/inconshreveable/mousetrap v1.1.0 // indirect
 	github.com/ipfs/boxo v0.27.2 // indirect
 	github.com/ipfs/go-cid v0.5.0 // indirect
-	github.com/ipfs/go-datastore v0.6.0 // indirect
+	github.com/ipfs/go-datastore v0.8.2 // indirect
 	github.com/ipfs/go-log/v2 v2.5.1 // indirect
 	github.com/ipld/go-ipld-prime v0.21.0 // indirect
 	github.com/jackpal/go-nat-pmp v1.0.2 // indirect
 	github.com/jbenet/go-temp-err-catcher v0.1.0 // indirect
-	github.com/jbenet/goprocess v0.1.4 // indirect
 	github.com/json-iterator/go v1.1.12 // indirect
-	github.com/klauspost/compress v1.17.11 // indirect
+	github.com/klauspost/compress v1.18.0 // indirect
 	github.com/kr/pretty v0.3.1 // indirect
 	github.com/kr/text v0.2.0 // indirect
 	github.com/mattn/go-colorable v0.1.13 // indirect
 	github.com/mattn/go-isatty v0.0.20 // indirect
 	github.com/mattn/go-runewidth v0.0.15 // indirect
-	github.com/miekg/dns v1.1.63 // indirect
+	github.com/miekg/dns v1.1.66 // indirect
 	github.com/mikioh/tcpinfo v0.0.0-20190314235526-30a79bb1804b // indirect
 	github.com/mikioh/tcpopt v0.0.0-20190314235656-172688c1accc // indirect
 	github.com/minio/sha256-simd v1.0.1 // indirect
 	github.com/mitchellh/colorstring v0.0.0-20190213212951-d06e56a500db // indirect
 	github.com/mitchellh/go-homedir v1.1.0 // indirect
 	github.com/mitchellh/mapstructure v1.5.0 // indirect
-	github.com/mmcloughlin/addchain v0.4.0 // indirect
 	github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd // indirect
 	github.com/modern-go/reflect2 v1.0.2 // indirect
 	github.com/mschoch/smat v0.2.0 // indirect
@@ -207,29 +199,29 @@ require (
 	github.com/pelletier/go-toml/v2 v2.2.1 // indirect
 	github.com/pion/datachannel v1.5.10 // indirect
 	github.com/pion/dtls/v2 v2.2.12 // indirect
-	github.com/pion/dtls/v3 v3.0.4 // indirect
+	github.com/pion/dtls/v3 v3.0.6 // indirect
 	github.com/pion/ice/v2 v2.3.37 // indirect
-	github.com/pion/ice/v4 v4.0.6 // indirect
-	github.com/pion/interceptor v0.1.37 // indirect
+	github.com/pion/ice/v4 v4.0.10 // indirect
+	github.com/pion/interceptor v0.1.40 // indirect
 	github.com/pion/logging v0.2.3 // indirect
 	github.com/pion/mdns v0.0.12 // indirect
 	github.com/pion/mdns/v2 v2.0.7 // indirect
 	github.com/pion/randutil v0.1.0 // indirect
 	github.com/pion/rtcp v1.2.15 // indirect
-	github.com/pion/rtp v1.8.11 // indirect
-	github.com/pion/sctp v1.8.35 // indirect
-	github.com/pion/sdp/v3 v3.0.10 // indirect
+	github.com/pion/rtp v1.8.19 // indirect
+	github.com/pion/sctp v1.8.39 // indirect
+	github.com/pion/sdp/v3 v3.0.13 // indirect
 	github.com/pion/srtp/v2 v2.0.20 // indirect
-	github.com/pion/srtp/v3 v3.0.4 // indirect
+	github.com/pion/srtp/v3 v3.0.6 // indirect
 	github.com/pion/stun v0.6.1 // indirect
 	github.com/pion/stun/v2 v2.0.0 // indirect
 	github.com/pion/stun/v3 v3.0.0 // indirect
 	github.com/pion/transport/v2 v2.2.10 // indirect
 	github.com/pion/transport/v3 v3.0.7 // indirect
 	github.com/pion/turn/v2 v2.1.6 // indirect
-	github.com/pion/turn/v4 v4.0.0 // indirect
+	github.com/pion/turn/v4 v4.0.2 // indirect
 	github.com/pion/webrtc/v3 v3.3.5 // indirect
-	github.com/pion/webrtc/v4 v4.0.8 // indirect
+	github.com/pion/webrtc/v4 v4.1.2 // indirect
 	github.com/rivo/uniseg v0.2.0 // indirect
 	github.com/rogpeppe/go-internal v1.13.1 // indirect
 	github.com/supranational/blst v0.3.15 // indirect
@@ -239,12 +231,11 @@ require (
 	github.com/ugorji/go/codec/codecgen v1.1.13 // indirect
 	github.com/wlynxg/anet v0.0.5 // indirect
 	go.opentelemetry.io/auto/sdk v1.1.0 // indirect
-	go.uber.org/dig v1.18.0 // indirect
-	go.uber.org/fx v1.23.0 // indirect
-	golang.org/x/mod v0.24.0 // indirect
-	golang.org/x/tools v0.31.0 // indirect
+	go.uber.org/dig v1.19.0 // indirect
+	go.uber.org/fx v1.24.0 // indirect
+	golang.org/x/mod v0.29.0 // indirect
+	golang.org/x/tools v0.38.0 // indirect
 	gonum.org/v1/gonum v0.15.1 // indirect
-	rsc.io/tmplfunc v0.0.3 // indirect
 )
 
 require (
@@ -256,15 +247,14 @@ require (
 	github.com/dustinxie/gmsm v1.4.0 // indirect
 	github.com/felixge/httpsnoop v1.0.4 // indirect
 	github.com/flynn/noise v1.1.0 // indirect
-	github.com/francoispqt/gojay v1.2.13 // indirect
 	github.com/fsnotify/fsnotify v1.6.0 // indirect
 	github.com/go-logr/logr v1.4.2 // indirect
 	github.com/go-logr/stdr v1.2.2 // indirect
 	github.com/go-ole/go-ole v1.3.0 // indirect
 	github.com/gogo/protobuf v1.3.2 // indirect
 	github.com/golang-jwt/jwt v3.2.2+incompatible // indirect
-	github.com/klauspost/cpuid/v2 v2.2.9 // indirect
-	github.com/koron/go-ssdp v0.0.5 // indirect
+	github.com/klauspost/cpuid/v2 v2.2.10 // indirect
+	github.com/koron/go-ssdp v0.0.6 // indirect
 	github.com/libp2p/go-buffer-pool v0.1.0 // indirect
 	github.com/libp2p/go-cidranger v1.1.0 // indirect
 	github.com/libp2p/go-flow-metrics v0.2.0 // indirect
@@ -274,10 +264,9 @@ require (
 	github.com/libp2p/go-libp2p-record v0.3.1 // indirect
 	github.com/libp2p/go-libp2p-routing-helpers v0.7.4 // indirect
 	github.com/libp2p/go-msgio v0.3.0 // indirect
-	github.com/libp2p/go-nat v0.2.0 // indirect
-	github.com/libp2p/go-netroute v0.2.2 // indirect
+	github.com/libp2p/go-netroute v0.3.0 // indirect
 	github.com/libp2p/go-reuseport v0.4.0 // indirect
-	github.com/libp2p/go-yamux/v4 v4.0.2 // indirect
+	github.com/libp2p/go-yamux/v5 v5.0.1 // indirect
 	github.com/lufia/plan9stats v0.0.0-20211012122336-39d0f177ccd0 // indirect
 	github.com/magefile/mage v1.9.0 // indirect
 	github.com/marten-seemann/tcp v0.0.0-20210406111302-dfbc87cc63fd // indirect
@@ -287,27 +276,26 @@ require (
 	github.com/multiformats/go-multiaddr-dns v0.4.1 // indirect
 	github.com/multiformats/go-multiaddr-fmt v0.1.0 // indirect
 	github.com/multiformats/go-multibase v0.2.0 // indirect
-	github.com/multiformats/go-multicodec v0.9.0 // indirect
+	github.com/multiformats/go-multicodec v0.9.1 // indirect
 	github.com/multiformats/go-multihash v0.2.3 // indirect
-	github.com/multiformats/go-multistream v0.6.0 // indirect
+	github.com/multiformats/go-multistream v0.6.1 // indirect
 	github.com/multiformats/go-varint v0.0.7 // indirect
 	github.com/olekukonko/tablewriter v0.0.5 // indirect
-	github.com/onsi/ginkgo/v2 v2.22.2 // indirect
+	github.com/onsi/gomega v1.36.2 // indirect
 	github.com/opencontainers/runtime-spec v1.2.0 // indirect
 	github.com/pbnjay/memory v0.0.0-20210728143218-7b4eea64cf58 // indirect
 	github.com/pierrec/lz4 v2.0.5+incompatible // indirect
 	github.com/pmezard/go-difflib v1.0.0 // indirect
 	github.com/polydawn/refmt v0.89.0 // indirect
 	github.com/power-devops/perfstat v0.0.0-20210106213030-5aafc221ea8c // indirect
-	github.com/prometheus/common v0.62.0 // indirect
-	github.com/prometheus/procfs v0.15.1 // indirect
+	github.com/prometheus/common v0.64.0 // indirect
+	github.com/prometheus/procfs v0.16.1 // indirect
 	github.com/protolambda/ztyp v0.2.2 // indirect
 	github.com/prysmaticlabs/gohashtree v0.0.3-alpha.0.20230502123415-aafd8b3ca202 // indirect
 	github.com/quasilyte/go-ruleguard/dsl v0.3.22 // indirect
-	github.com/quic-go/qpack v0.5.1 // indirect
-	github.com/quic-go/quic-go v0.49.0 // indirect
-	github.com/quic-go/webtransport-go v0.8.1-0.20241018022711-4ac2c9250e66 // indirect
-	github.com/raulk/go-watchdog v1.3.0 // indirect
+	github.com/quic-go/qpack v0.6.0 // indirect
+	github.com/quic-go/quic-go v0.57.1 // indirect
+	github.com/quic-go/webtransport-go v0.9.0 // indirect
 	github.com/remyoudompheng/bigfft v0.0.0-20230129092748-24d4a6f8daec // indirect
 	github.com/rs/dnscache v0.0.0-20211102005908-e0241e321417 // indirect
 	github.com/ryanuber/go-glob v1.0.0 // indirect
@@ -317,7 +305,7 @@ require (
 	github.com/sirupsen/logrus v1.9.3 // indirect
 	github.com/spaolacci/murmur3 v1.1.0 // indirect
 	github.com/spf13/afero v1.9.5 // indirect
-	github.com/spf13/pflag v1.0.5 // indirect
+	github.com/spf13/pflag v1.0.6 // indirect
 	github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7 // indirect
 	github.com/tidwall/match v1.1.1 // indirect
 	github.com/tidwall/pretty v1.2.0 // indirect
@@ -331,13 +319,14 @@ require (
 	go.opencensus.io v0.24.0 // indirect
 	go.opentelemetry.io/otel/metric v1.34.0 // indirect
 	go.uber.org/multierr v1.11.0 // indirect
-	golang.org/x/exp v0.0.0-20250305212735-054e65f0b394 // indirect
-	golang.org/x/sys v0.31.0 // indirect
-	golang.org/x/term v0.30.0 // indirect
+	golang.org/x/exp v0.0.0-20250606033433-dcc06ee1d476 // indirect
+	golang.org/x/sys v0.38.0 // indirect
+	golang.org/x/telemetry v0.0.0-20251008203120-078029d740a8 // indirect
+	golang.org/x/term v0.37.0 // indirect
 	google.golang.org/grpc/cmd/protoc-gen-go-grpc v1.3.0 // indirect
 	gopkg.in/square/go-jose.v2 v2.5.1 // indirect
 	gopkg.in/yaml.v3 v3.0.1 // indirect
-	lukechampine.com/blake3 v1.3.0 // indirect
+	lukechampine.com/blake3 v1.4.1 // indirect
 	modernc.org/libc v1.62.1 // indirect
 	modernc.org/mathutil v1.7.1 // indirect
 	modernc.org/memory v1.9.1 // indirect
@@ -361,3 +350,6 @@ replace github.com/gballet/go-verkle => github.com/envestcc/go-verkle v0.0.0-202
 replace github.com/erigontech/erigon-snapshot => github.com/ledgerwatch/erigon-snapshot v1.3.1-0.20240805114253-42da880260bb
 
 replace github.com/ethereum/go-ethereum/crypto/secp256k1 => github.com/erigontech/secp256k1 v1.1.0
+
+// Fix for go-libutp compatibility with GCC 15+
+replace github.com/anacrolix/go-libutp => github.com/anacrolix/go-libutp v0.0.0-20251121015447-f294e5ed5b4d
```

### go.sum
```diff
@@ -1,7 +1,5 @@
 cloud.google.com/go v0.26.0/go.mod h1:aQUYkXzVsufM+DwF1aE+0xfcU+56JwCaLick0ClmMTw=
-cloud.google.com/go v0.31.0/go.mod h1:aQUYkXzVsufM+DwF1aE+0xfcU+56JwCaLick0ClmMTw=
 cloud.google.com/go v0.34.0/go.mod h1:aQUYkXzVsufM+DwF1aE+0xfcU+56JwCaLick0ClmMTw=
-cloud.google.com/go v0.37.0/go.mod h1:TS1dMSSfndXH133OKGwekG838Om/cQT0BUHV3HcBgoo=
 cloud.google.com/go v0.38.0/go.mod h1:990N+gfupTy94rShfmMCWGDn0LpTmnzTp2qbd1dvSRU=
 cloud.google.com/go v0.44.1/go.mod h1:iSa0KzasP4Uvy3f1mN/7PiObzGgflwredwwASm/v6AU=
 cloud.google.com/go v0.44.2/go.mod h1:60680Gw3Yr4ikxnPRS/oxxkBccT6SA1yMk63TGekxKY=
@@ -41,14 +39,9 @@ crawshaw.io/iox v0.0.0-20181124134642-c51c3df30797/go.mod h1:sXBiorCo8c46JlQV3oX
 crawshaw.io/sqlite v0.3.2/go.mod h1:igAO5JulrQ1DbdZdtVq48mnZUBAPOeFzer7VhDWNtW4=
 dario.cat/mergo v1.0.2 h1:85+piFYR1tMbRrLcDwR18y4UKJ3aH1Tbzi24VRW1TK8=
 dario.cat/mergo v1.0.2/go.mod h1:E/hbnu0NxMFBjpMIE34DRGLWqDy0g5FuKDhCb31ngxA=
-dmitri.shuralyov.com/app/changes v0.0.0-20180602232624-0a106ad413e3/go.mod h1:Yl+fi1br7+Rr3LqpNJf1/uxUdtRUV+Tnj0o93V2B9MU=
 dmitri.shuralyov.com/gpu/mtl v0.0.0-20190408044501-666a987793e9/go.mod h1:H6x//7gZCb22OMCxBHrMx7a5I7Hp++hsVxbQ4BYO7hU=
-dmitri.shuralyov.com/html/belt v0.0.0-20180602232347-f7d459c86be0/go.mod h1:JLBrvjyP0v+ecvNYvCpyZgu5/xkfAUhi6wJj28eUfSU=
-dmitri.shuralyov.com/service/change v0.0.0-20181023043359-a85b471d5412/go.mod h1:a1inKt/atXimZ4Mv927x+r7UpyzRUf4emIoiiSC2TN4=
-dmitri.shuralyov.com/state v0.0.0-20180228185332-28bcc343414c/go.mod h1:0PRwlb0D6DFvNNtx+9ybjezNCa8XF0xaYcETyp6rHWU=
 filippo.io/edwards25519 v1.0.0-rc.1 h1:m0VOOB23frXZvAOK44usCgLWvtsxIoMCTBGJZlpmGfU=
 filippo.io/edwards25519 v1.0.0-rc.1/go.mod h1:N1IkdkCkiLB6tki+MYJoSx2JTY9NUlxZE7eHn5EwJns=
-git.apache.org/thrift.git v0.0.0-20180902110319-2566ecd5d999/go.mod h1:fPE2ZNJGynbRyZ4dJvy6G277gSllfV2HJqblrnkyeyg=
 github.com/BurntSushi/toml v0.3.1/go.mod h1:xHWCNGjB5oqiDr8zfno3MHue2Ht5sIBksp03qcyfWMU=
 github.com/BurntSushi/xgb v0.0.0-20160522181843-27f122750802/go.mod h1:IVnqGOEym/WlBOVXweHU+Q+/VP0lqqI8lqeDx9IjBqo=
 github.com/DataDog/datadog-go v3.2.0+incompatible/go.mod h1:LButxg5PwREeZtORoXG3tL4fMGNddJ+vMq1mwgfaqoQ=
@@ -97,8 +90,8 @@ github.com/anacrolix/envpprof v1.3.0 h1:WJt9bpuT7A/CDCxPOv/eeZqHWlle/Y0keJUvc6tc
 github.com/anacrolix/envpprof v1.3.0/go.mod h1:7QIG4CaX1uexQ3tqd5+BRa/9e2D02Wcertl6Yh0jCB0=
 github.com/anacrolix/generics v0.0.0-20230816105729-c755655aee45 h1:Kmcl3I9K2+5AdnnR7hvrnVT0TLeFWWMa9bxnm55aVIg=
 github.com/anacrolix/generics v0.0.0-20230816105729-c755655aee45/go.mod h1:ff2rHB/joTV03aMSSn/AZNnaIpUw0h3njetGsaXcMy8=
-github.com/anacrolix/go-libutp v1.3.1 h1:idJzreNLl+hNjGC3ZnUOjujEaryeOGgkwHLqSGoige0=
-github.com/anacrolix/go-libutp v1.3.1/go.mod h1:heF41EC8kN0qCLMokLBVkB8NXiLwx3t8R8810MTNI5o=
+github.com/anacrolix/go-libutp v0.0.0-20251121015447-f294e5ed5b4d h1:V4OeJvKDh/lixhYRNWnb1MgfTOn/7MFEdOBIgwgMFhk=
+github.com/anacrolix/go-libutp v0.0.0-20251121015447-f294e5ed5b4d/go.mod h1:2XL3ViU/7+l/kB6poGICETXdEVRdTALyqQrKFBCkBc4=
 github.com/anacrolix/log v0.3.0/go.mod h1:lWvLTqzAnCWPJA08T2HCstZi0L1y2Wyvm3FJgwU9jwU=
 github.com/anacrolix/log v0.6.0/go.mod h1:lWvLTqzAnCWPJA08T2HCstZi0L1y2Wyvm3FJgwU9jwU=
 github.com/anacrolix/log v0.10.1-0.20220123034749-3920702c17f8/go.mod h1:GmnE2c0nvz8pOIPUSC9Rawgefy1sDXqposC2wgtBZE4=
@@ -118,17 +111,15 @@ github.com/anacrolix/missinggo/perf v1.0.0/go.mod h1:ljAFWkBuzkO12MQclXzZrosP5ur
 github.com/anacrolix/missinggo/v2 v2.2.0/go.mod h1:o0jgJoYOyaoYQ4E2ZMISVa9c88BbUBVQQW4QeRkNCGY=
 github.com/anacrolix/missinggo/v2 v2.5.1/go.mod h1:WEjqh2rmKECd0t1VhQkLGTdIWXO6f6NLjp5GlMZ+6FA=
 github.com/anacrolix/missinggo/v2 v2.5.2/go.mod h1:yNvsLrtZYRYCOI+KRH/JM8TodHjtIE/bjOGhQaLOWIE=
-github.com/anacrolix/missinggo/v2 v2.7.2-0.20230527121029-a582b4f397b9 h1:W/oGeHhYwxueeiDjQfmK9G+X9M2xJgfTtow62v0TWAs=
-github.com/anacrolix/missinggo/v2 v2.7.2-0.20230527121029-a582b4f397b9/go.mod h1:mIEtp9pgaXqt8VQ3NQxFOod/eQ1H0D1XsZzKUQfwtac=
-github.com/anacrolix/mmsg v0.0.0-20180515031531-a4a3ba1fc8bb/go.mod h1:x2/ErsYUmT77kezS63+wzZp8E3byYB0gzirM/WMBLfw=
-github.com/anacrolix/mmsg v1.0.0 h1:btC7YLjOn29aTUAExJiVUhQOuf/8rhm+/nWCMAnL3Hg=
-github.com/anacrolix/mmsg v1.0.0/go.mod h1:x8kRaJY/dCrY9Al0PEcj1mb/uFHwP6GCJ9fLl4thEPc=
+github.com/anacrolix/missinggo/v2 v2.10.0 h1:pg0iO4Z/UhP2MAnmGcaMtp5ZP9kyWsusENWN9aolrkY=
+github.com/anacrolix/missinggo/v2 v2.10.0/go.mod h1:nCRMW6bRCMOVcw5z9BnSYKF+kDbtenx+hQuphf4bK8Y=
+github.com/anacrolix/mmsg v1.0.1 h1:TxfpV7kX70m3f/O7ielL/2I3OFkMPjrRCPo7+4X5AWw=
+github.com/anacrolix/mmsg v1.0.1/go.mod h1:x8kRaJY/dCrY9Al0PEcj1mb/uFHwP6GCJ9fLl4thEPc=
 github.com/anacrolix/multiless v0.3.1-0.20221221005021-2d12701f83f7 h1:lOtCD+LzoD1g7bowhYJNR++uV+FyY5bTZXKwnPex9S8=
 github.com/anacrolix/multiless v0.3.1-0.20221221005021-2d12701f83f7/go.mod h1:zJv1JF9AqdZiHwxqPgjuOZDGWER6nyE48WBCi/OOrMM=
 github.com/anacrolix/stm v0.2.0/go.mod h1:zoVQRvSiGjGoTmbM0vSLIiaKjWtNPeTvXUSdJQA4hsg=
-github.com/anacrolix/stm v0.4.1-0.20221221005312-96d17df0e496 h1:aMiRi2kOOd+nG64suAmFMVnNK2E6GsnLif7ia9tI3cA=
-github.com/anacrolix/stm v0.4.1-0.20221221005312-96d17df0e496/go.mod h1:DBm8/1OXm4A4RZ6Xa9u/eOsjeAXCaoRYvd2JzlskXeM=
-github.com/anacrolix/sync v0.0.0-20180808010631-44578de4e778/go.mod h1:s735Etp3joe/voe2sdaXLcqDdJSay1O0OPnM0ystjqk=
+github.com/anacrolix/stm v0.5.0 h1:9df1KBpttF0TzLgDq51Z+TEabZKMythqgx89f1FQJt8=
+github.com/anacrolix/stm v0.5.0/go.mod h1:MOwrSy+jCm8Y7HYfMAwPj7qWVu7XoVvjOiYwJmpeB/M=
 github.com/anacrolix/sync v0.3.0/go.mod h1:BbecHL6jDSExojhNtgTFSBcdGerzNc64tz3DCOj/I0g=
 github.com/anacrolix/sync v0.5.1 h1:FbGju6GqSjzVoTgcXTUKkF041lnZkG5P0C3T5RL3SGc=
 github.com/anacrolix/sync v0.5.1/go.mod h1:BbecHL6jDSExojhNtgTFSBcdGerzNc64tz3DCOj/I0g=
@@ -141,15 +132,13 @@ github.com/anacrolix/upnp v0.1.3-0.20220123035249-922794e51c96 h1:QAVZ3pN/J4/Uzi
 github.com/anacrolix/upnp v0.1.3-0.20220123035249-922794e51c96/go.mod h1:Wa6n8cYIdaG35x15aH3Zy6d03f7P728QfdcDeD/IEOs=
 github.com/anacrolix/utp v0.1.0 h1:FOpQOmIwYsnENnz7tAGohA+r6iXpRjrq8ssKSre2Cp4=
 github.com/anacrolix/utp v0.1.0/go.mod h1:MDwc+vsGEq7RMw6lr2GKOEqjWny5hO5OZXRVNaBJ2Dk=
-github.com/anmitsu/go-shlex v0.0.0-20161002113705-648efa622239/go.mod h1:2FmKhYUyUczH0OGQWaF5ceTx0UBShxjsH6f8oGKYe2c=
 github.com/apache/thrift v0.12.0/go.mod h1:cp2SuWMxlEZw2r+iP2GNCdIi4C1qmUzdZFSVb+bacwQ=
 github.com/armon/go-metrics v0.3.0/go.mod h1:zXjbSimjXTd7vOpY8B0/2LpvNvDoXBuplAD+gJD3GYs=
 github.com/armon/go-radix v0.0.0-20180808171621-7fddfc383310/go.mod h1:ufUuZ+zHj4x4TnLV4JWEpy2hxWSpsRywHrMgIH9cCH8=
 github.com/aws/aws-sdk-go v1.25.37/go.mod h1:KmX6BPdI08NWTb3/sm4ZGu5ShLoqVDhKgpiN924inxo=
 github.com/bahlo/generic-list-go v0.2.0 h1:5sz/EEAK+ls5wF+NeqDpk5+iNdMDXrh3z3nPnH1Wvgk=
 github.com/bahlo/generic-list-go v0.2.0/go.mod h1:2KvAjgMlE5NNynlg/5iLrrCCZ2+5xWbdbCW3pNTGyYg=
 github.com/benbjohnson/clock v1.1.0/go.mod h1:J11/hYXuz8f4ySSvYwY0FKfm+ezbsZBKZxNJlLklBHA=
-github.com/benbjohnson/clock v1.3.0/go.mod h1:J11/hYXuz8f4ySSvYwY0FKfm+ezbsZBKZxNJlLklBHA=
 github.com/benbjohnson/clock v1.3.5 h1:VvXlSJBzZpA/zum6Sj74hxwYI2DIxRWuNIoXAzHZz5o=
 github.com/benbjohnson/clock v1.3.5/go.mod h1:J11/hYXuz8f4ySSvYwY0FKfm+ezbsZBKZxNJlLklBHA=
 github.com/benbjohnson/immutable v0.2.0/go.mod h1:uc6OHo6PN2++n98KHLxW8ef4W42ylHiQSENghE1ezxI=
@@ -167,7 +156,6 @@ github.com/bits-and-blooms/bitset v1.20.0 h1:2F+rfL86jE2d/bmw7OhqUg2Sj/1rURkBn3M
 github.com/bits-and-blooms/bitset v1.20.0/go.mod h1:7hO7Gc7Pp1vODcmWvKMRA9BNmbv6a/7QIWpPxHddWR8=
 github.com/blang/semver/v4 v4.0.0 h1:1PFHFE6yCCTv8C1TeyNNarDzntLi7wMI5i/pzqYIsAM=
 github.com/blang/semver/v4 v4.0.0/go.mod h1:IbckMUScFkM3pff0VJDNKRiT6TG/YpiHIM2yvyW5YoQ=
-github.com/bradfitz/go-smtpd v0.0.0-20170404230938-deb6d6237625/go.mod h1:HYsPBTaaSFSlLx/70C2HPIMNZpVV8+vt/A+FMnYP11g=
 github.com/bradfitz/iter v0.0.0-20140124041915-454541ec3da2/go.mod h1:PyRFw1Lt2wKX4ZVSQ2mk+PeDa1rxyObEDlApuIsUKuo=
 github.com/bradfitz/iter v0.0.0-20190303215204-33e6a9893b0c/go.mod h1:PyRFw1Lt2wKX4ZVSQ2mk+PeDa1rxyObEDlApuIsUKuo=
 github.com/bradfitz/iter v0.0.0-20191230175014-e8f45d346db8 h1:GKTyiRCL6zVf5wWaqKnf+7Qs6GbEPfd4iMOitWzXJx8=
@@ -200,7 +188,6 @@ github.com/btcsuite/snappy-go v0.0.0-20151229074030-0bdef8d06723/go.mod h1:8woku
 github.com/btcsuite/snappy-go v1.0.0/go.mod h1:8woku9dyThutzjeg+3xrA5iCpBRH8XEEg3lh6TiUghc=
 github.com/btcsuite/websocket v0.0.0-20150119174127-31079b680792/go.mod h1:ghJtEyQwv5/p4Mg4C0fgbePVuGr935/5ddU9Z3TmDRY=
 github.com/btcsuite/winsvc v1.0.0/go.mod h1:jsenWakMcC0zFBFurPLEAyrnc/teJEM1O46fmI40EZs=
-github.com/buger/jsonparser v0.0.0-20181115193947-bf1c66bbce23/go.mod h1:bbYlZJ7hK1yFx9hf58LP0zeX7UjIGs20ufpu3evjr+s=
 github.com/c2h5oh/datasize v0.0.0-20231215233829-aa82cc1e6500 h1:6lhrsTEnloDPXyeZBvSYvQf8u86jbKehZPVDDlkgDl4=
 github.com/c2h5oh/datasize v0.0.0-20231215233829-aa82cc1e6500/go.mod h1:S/7n9copUssQ56c7aAgHqftWO4LTf4xY6CGWt8Bc+3M=
 github.com/cenkalti/backoff v2.2.1+incompatible h1:tNowT99t7UNflLxfYYSlKYsBpXdEet03Pg2g16Swow4=
@@ -220,7 +207,6 @@ github.com/chzyer/readline v0.0.0-20180603132655-2972be24d48e/go.mod h1:nSuG5e5P
 github.com/chzyer/readline v1.5.0/go.mod h1:x22KAscuvRqlLoK9CsoYsmxoXZMMFVyOl86cAH8qUic=
 github.com/chzyer/test v0.0.0-20180213035817-a1ea475d72b1/go.mod h1:Q3SI9o4m/ZMnBNeIyt5eFwwo7qiLfzFZmjNmxjkiQlU=
 github.com/chzyer/test v0.0.0-20210722231415-061457976a23/go.mod h1:Q3SI9o4m/ZMnBNeIyt5eFwwo7qiLfzFZmjNmxjkiQlU=
-github.com/cilium/ebpf v0.2.0/go.mod h1:To2CFviqOWL/M0gIMsvSMlqe7em/l1ALkX1PyjrX2Qs=
 github.com/cilium/ebpf v0.11.0 h1:V8gS/bTCCjX9uUnkUFUpPsksM8n1lXBAvHcpiFk1X2Y=
 github.com/cilium/ebpf v0.11.0/go.mod h1:WE7CZAnqOL2RouJ4f1uyNhqr2P4CCvXFIqdRDUgWsVs=
 github.com/circonus-labs/circonus-gometrics v2.3.1+incompatible/go.mod h1:nmEj6Dob7S7YxXgwXpfOuvO54S+tGdZdw9fuRZt25Ag=
@@ -243,21 +229,13 @@ github.com/cockroachdb/redact v1.1.5 h1:u1PMllDkdFfPWaNGMyLD1+so+aq3uUItthCFqzwP
 github.com/cockroachdb/redact v1.1.5/go.mod h1:BVNblN9mBWFyMyqK1k3AAiSxhvhfK2oOZZ2lK+dpvRg=
 github.com/cockroachdb/tokenbucket v0.0.0-20230807174530-cc333fc44b06 h1:zuQyyAKVxetITBuuhv3BI9cMrmStnpT18zmgmTxunpo=
 github.com/cockroachdb/tokenbucket v0.0.0-20230807174530-cc333fc44b06/go.mod h1:7nc4anLGjupUW/PeY5qiNYsdNXj7zopG+eqsS7To5IQ=
-github.com/consensys/bavard v0.1.27 h1:j6hKUrGAy/H+gpNrpLU3I26n1yc+VMGmd6ID5+gAhOs=
-github.com/consensys/bavard v0.1.27/go.mod h1:k/zVjHHC4B+PQy1Pg7fgvG3ALicQw540Crag8qx+dZs=
-github.com/consensys/gnark-crypto v0.16.0 h1:8Dl4eYmUWK9WmlP1Bj6je688gBRJCJbT8Mw4KoTAawo=
-github.com/consensys/gnark-crypto v0.16.0/go.mod h1:Ke3j06ndtPTVvo++PhGNgvm+lgpLvzbcE2MqljY7diU=
-github.com/containerd/cgroups v0.0.0-20201119153540-4cbc285b3327/go.mod h1:ZJeTFisyysqgcCdecO57Dj79RfL0LNeGiFUqLYQRYLE=
-github.com/containerd/cgroups v1.1.0 h1:v8rEWFl6EoqHB+swVNjVoCJE8o3jX7e8nqBGPLaDFBM=
-github.com/containerd/cgroups v1.1.0/go.mod h1:6ppBcbh/NOOUU+dMKrykgaBnK9lCIBxHqJDGwsa1mIw=
+github.com/consensys/gnark-crypto v0.18.1 h1:RyLV6UhPRoYYzaFnPQA4qK3DyuDgkTgskDdoGqFt3fI=
+github.com/consensys/gnark-crypto v0.18.1/go.mod h1:L3mXGFTe1ZN+RSJ+CLjUt9x7PNdx8ubaYfDROyp2Z8c=
 github.com/containerd/cgroups/v3 v3.0.3 h1:S5ByHZ/h9PMe5IOQoN7E+nMc2UcLEM/V48DGDJ9kip0=
 github.com/containerd/cgroups/v3 v3.0.3/go.mod h1:8HBe7V3aWGLFPd/k03swSIsGjZhHI2WzJmticMgVuz0=
-github.com/coreos/go-systemd v0.0.0-20181012123002-c6f51f82210d/go.mod h1:F5haX7vjVVG0kc13fIWeqUViNPyEJxv/OmvnBo0Yme4=
-github.com/coreos/go-systemd/v22 v22.1.0/go.mod h1:xO0FLkIi5MaZafQlIrOotqXZ90ih+1atmu1JpKERPPk=
 github.com/coreos/go-systemd/v22 v22.5.0 h1:RrqgGjYQKalulkV8NGVIfkXQf6YYmOyiJKk8iXXhfZs=
 github.com/coreos/go-systemd/v22 v22.5.0/go.mod h1:Y58oyj3AT4RCenI/lSvhwexgC+NSVTIJ3seZv2GcEnc=
 github.com/cpuguy83/go-md2man/v2 v2.0.0-20190314233015-f79a8a8ca69d/go.mod h1:maD7wRr/U5Z6m/iR4s+kqSMx2CaBsrgA7czyZG/E6dU=
-github.com/cpuguy83/go-md2man/v2 v2.0.0/go.mod h1:maD7wRr/U5Z6m/iR4s+kqSMx2CaBsrgA7czyZG/E6dU=
 github.com/cpuguy83/go-md2man/v2 v2.0.4/go.mod h1:tgQtvFlXSQOSOSIRvRPT7W67SCa46tRHOmNcaadrF8o=
 github.com/cpuguy83/go-md2man/v2 v2.0.5 h1:ZtcqGrnekaHpVLArFSe4HK5DoKx1T0rq2DwVB0alcyc=
 github.com/cpuguy83/go-md2man/v2 v2.0.5/go.mod h1:tgQtvFlXSQOSOSIRvRPT7W67SCa46tRHOmNcaadrF8o=
@@ -281,11 +259,11 @@ github.com/deckarep/golang-set v1.8.0/go.mod h1:5nI87KwE7wgsBU1F4GKAw2Qod7p5kyS3
 github.com/deckarep/golang-set/v2 v2.6.0 h1:XfcQbWM1LlMB8BsJ8N9vW5ehnnPVIw0je80NsVHagjM=
 github.com/deckarep/golang-set/v2 v2.6.0/go.mod h1:VAky9rY/yGXJOLEDv3OMci+7wtDpOF4IN+y82NBOac4=
 github.com/decred/dcrd/crypto/blake256 v1.0.0/go.mod h1:sQl2p6Y26YV+ZOcSTP6thNdn47hh8kt6rqSlvmrXFAc=
-github.com/decred/dcrd/crypto/blake256 v1.0.1 h1:7PltbUIQB7u/FfZ39+DGa/ShuMyJ5ilcvdfma9wOH6Y=
-github.com/decred/dcrd/crypto/blake256 v1.0.1/go.mod h1:2OfgNZ5wDpcsFmHmCK5gZTPcCXqlm2ArzUIkw9czNJo=
+github.com/decred/dcrd/crypto/blake256 v1.1.0 h1:zPMNGQCm0g4QTY27fOCorQW7EryeQ/U0x++OzVrdms8=
+github.com/decred/dcrd/crypto/blake256 v1.1.0/go.mod h1:2OfgNZ5wDpcsFmHmCK5gZTPcCXqlm2ArzUIkw9czNJo=
 github.com/decred/dcrd/dcrec/secp256k1/v4 v4.0.1/go.mod h1:hyedUtir6IdtD/7lIxGeCxkaw7y45JueMRL4DIyJDKs=
-github.com/decred/dcrd/dcrec/secp256k1/v4 v4.3.0 h1:rpfIENRNNilwHwZeG5+P150SMrnNEcHYvcCuK6dPZSg=
-github.com/decred/dcrd/dcrec/secp256k1/v4 v4.3.0/go.mod h1:v57UDF4pDQJcEfFUCRop3lJL149eHGSe9Jvczhzjo/0=
+github.com/decred/dcrd/dcrec/secp256k1/v4 v4.4.0 h1:NMZiJj8QnKe1LgsbDayM4UoHwbvwDRwnI3hwNaAHRnc=
+github.com/decred/dcrd/dcrec/secp256k1/v4 v4.4.0/go.mod h1:ZXNYxsqcloTdSy/rNShjYzMhyjf0LaoftYK0p+A3h40=
 github.com/decred/dcrd/lru v1.0.0/go.mod h1:mxKOwFd7lFjN2GZYsiz/ecgqR6kkYAl+0pz0tEMk218=
 github.com/deepmap/oapi-codegen v1.6.0 h1:w/d1ntwh91XI0b/8ja7+u5SvA4IFfM0UNNLmiDR1gg0=
 github.com/deepmap/oapi-codegen v1.6.0/go.mod h1:ryDa9AgbELGeB+YEXE1dR53yAjHwFvE9iAUlWl9Al3M=
@@ -294,7 +272,6 @@ github.com/dgryski/go-rendezvous v0.0.0-20200823014737-9f7001d12a5f/go.mod h1:cu
 github.com/dlclark/regexp2 v1.4.1-0.20201116162257-a2a8dda75c91/go.mod h1:2pZnwuY/m+8K6iRw6wQdMtk+rH5tNGR1i55kozfMjCc=
 github.com/dlclark/regexp2 v1.7.0 h1:7lJfhqlPssTb1WQx4yvTHN0uElPEv52sbaECrAQxjAo=
 github.com/dlclark/regexp2 v1.7.0/go.mod h1:DHkYz0B9wPfa6wondMfaivmHpzrQ3v9q8cnmRbL6yW8=
-github.com/docker/go-units v0.4.0/go.mod h1:fgPhTUdO+D/Jk86RDLlptpiXQzgHJF7gydDDbaIK4Dk=
 github.com/docker/go-units v0.5.0 h1:69rxXcBk27SvSaaxTtLh/8llcHD8vYHT7WSdRZ/jvr4=
 github.com/docker/go-units v0.5.0/go.mod h1:fgPhTUdO+D/Jk86RDLlptpiXQzgHJF7gydDDbaIK4Dk=
 github.com/docopt/docopt-go v0.0.0-20180111231733-ee0de3bc6815/go.mod h1:WwZ+bS3ebgob9U8Nd0kOddGdZWjyMGR8Wziv+TBNwSE=
@@ -314,9 +291,6 @@ github.com/eapache/go-xerial-snappy v0.0.0-20180814174437-776d5712da21/go.mod h1
 github.com/eapache/queue v1.1.0/go.mod h1:6eCeP0CKFpHLu8blIFXhExK/dRa7WDZfr6jVFPTqq+I=
 github.com/edsrzf/mmap-go v1.1.0 h1:6EUwBLQ/Mcr1EYLE4Tn1VdW1A4ckqCQWZBw8Hr0kjpQ=
 github.com/edsrzf/mmap-go v1.1.0/go.mod h1:19H/e8pUPLicwkyNgOykDXkJ9F0MHE+Z52B8EIth78Q=
-github.com/elastic/gosigar v0.12.0/go.mod h1:iXRIGg2tLnu7LBdpqzyQfGDEidKCfWcCMS0WKyPWoMs=
-github.com/elastic/gosigar v0.14.3 h1:xwkKwPia+hSfg9GqrCUKYdId102m9qTJIIr7egmK/uo=
-github.com/elastic/gosigar v0.14.3/go.mod h1:iXRIGg2tLnu7LBdpqzyQfGDEidKCfWcCMS0WKyPWoMs=
 github.com/emicklei/dot v1.6.1 h1:ujpDlBkkwgWUY+qPId5IwapRW/xEoligRSYjioR6DFI=
 github.com/emicklei/dot v1.6.1/go.mod h1:DeV7GvQtIw4h2u73RKBkkFdvVAz0D9fzeJrgPW6gy/s=
 github.com/envestcc/erigon v0.0.0-20251229032433-18f245cc374a h1:k+/OV4d1LRnuYgNg+mQX2gfpNoehZwdUnbx+RICEgTA=
@@ -357,12 +331,8 @@ github.com/ferranbt/fastssz v0.1.2 h1:Dky6dXlngF6Qjc+EfDipAkE83N5I5DE68bY6O0VLNP
 github.com/ferranbt/fastssz v0.1.2/go.mod h1:X5UPrE2u1UJjxHA8X54u04SBwdAQjG2sFtWs39YxyWs=
 github.com/fjl/gencodec v0.1.0 h1:B3K0xPfc52cw52BBgUbSPxYo+HlLfAgWMVKRWXUXBcs=
 github.com/fjl/gencodec v0.1.0/go.mod h1:Um1dFHPONZGTHog1qD1NaWjXJW/SPB38wPv0O8uZ2fI=
-github.com/flynn/go-shlex v0.0.0-20150515145356-3f9db97f8568/go.mod h1:xEzjJPgXI435gkrCt3MPfRiAkVrwSbHsst4LCFVfpJc=
 github.com/flynn/noise v1.1.0 h1:KjPQoQCEFdZDiP03phOvGi11+SVVhBG2wOWAorLsstg=
 github.com/flynn/noise v1.1.0/go.mod h1:xbMo+0i6+IGbYdJhF31t2eR1BIU0CYc12+BNAKwUTag=
-github.com/francoispqt/gojay v1.2.13 h1:d2m3sFjloqoIUQU3TsHBgj6qg/BVGlTBeHDUmyJnXKk=
-github.com/francoispqt/gojay v1.2.13/go.mod h1:ehT5mTG4ua4581f1++1WLG0vPdaA9HaiDsoyrBGkyDY=
-github.com/frankban/quicktest v1.9.0/go.mod h1:ui7WezCLWMWxVWr1GETZY3smRy0G4KWq9vcPtJmFl7Y=
 github.com/frankban/quicktest v1.14.6 h1:7Xjx+VpznH+oBnejlPUj8oUpdxnVs4f8XU8WnHkI4W8=
 github.com/frankban/quicktest v1.14.6/go.mod h1:4ptaffx2x8+WTWXmUCuVU6aPUX1/Mz7zb5vbUoiM6w0=
 github.com/fsnotify/fsnotify v1.4.7/go.mod h1:jwhsz4b93w/PPRr/qN1Yymfu8t87LnFCMoQvtojpjFo=
@@ -375,16 +345,13 @@ github.com/gballet/go-libpcsclite v0.0.0-20190607065134-2772fd86a8ff h1:tY80oXqG
 github.com/gballet/go-libpcsclite v0.0.0-20190607065134-2772fd86a8ff/go.mod h1:x7DCsMOv1taUwEWCzT4cmDeAkigA5/QCwUodaVOe8Ww=
 github.com/getsentry/sentry-go v0.27.0 h1:Pv98CIbtB3LkMWmXi4Joa5OOcwbmnX88sF5qbK3r3Ps=
 github.com/getsentry/sentry-go v0.27.0/go.mod h1:lc76E2QywIyW8WuBnwl8Lc4bkmQH4+w1gwTf25trprY=
-github.com/ghodss/yaml v1.0.0/go.mod h1:4dBDuWmgqj2HViK6kFavaiC9ZROes6MMH2rRYeMEF04=
-github.com/gliderlabs/ssh v0.1.1/go.mod h1:U7qILu1NlMHj9FlMhZLlkCdDnU1DBEAqr0aevW3Awn0=
 github.com/glycerine/go-unsnap-stream v0.0.0-20180323001048-9f0cb55181dd/go.mod h1:/20jfyN9Y5QPEAprSgKAUr+glWDY39ZiUEAYOEv5dsE=
 github.com/glycerine/go-unsnap-stream v0.0.0-20181221182339-f9677308dec2/go.mod h1:/20jfyN9Y5QPEAprSgKAUr+glWDY39ZiUEAYOEv5dsE=
 github.com/glycerine/go-unsnap-stream v0.0.0-20190901134440-81cf024a9e0a/go.mod h1:/20jfyN9Y5QPEAprSgKAUr+glWDY39ZiUEAYOEv5dsE=
 github.com/glycerine/goconvey v0.0.0-20180728074245-46e3a41ad493/go.mod h1:Ogl1Tioa0aV7gstGFO7KhffUsb9M4ydbEbbxpcEDc24=
 github.com/glycerine/goconvey v0.0.0-20190315024820-982ee783a72e/go.mod h1:Ogl1Tioa0aV7gstGFO7KhffUsb9M4ydbEbbxpcEDc24=
 github.com/glycerine/goconvey v0.0.0-20190410193231-58a59202ab31/go.mod h1:Ogl1Tioa0aV7gstGFO7KhffUsb9M4ydbEbbxpcEDc24=
 github.com/go-asn1-ber/asn1-ber v1.3.1/go.mod h1:hEBeB/ic+5LoWskz+yKT7vGhhPYkProFKoKdwZRWMe0=
-github.com/go-errors/errors v1.0.1/go.mod h1:f4zRHt4oKfwPJE5k8C9vpYG+aDHdBFUsgrm6/TyX73Q=
 github.com/go-errors/errors v1.4.2 h1:J6MZopCL4uSllY1OfXM374weqZFFItUbrImctkmUxIA=
 github.com/go-errors/errors v1.4.2/go.mod h1:sIVyrIiJhuEF+Pj9Ebtd6P/rEYROXFi3BopGUQ5a5Og=
 github.com/go-gl/glfw v0.0.0-20190409004039-e6da0acd62b1/go.mod h1:vR7hzQXu2zJy9AVAgeJqvqgH9Q5CA+iKCZ2gyEVpxRU=
@@ -419,36 +386,31 @@ github.com/go-sourcemap/sourcemap v2.1.3+incompatible/go.mod h1:F8jJfvm2KbVjc5Nq
 github.com/go-stack/stack v1.8.0/go.mod h1:v0f6uXyyMGvRgIKkXu+yp6POWl0qKG85gN/melR3HDY=
 github.com/go-stack/stack v1.8.1 h1:ntEHSVwIt7PNXNpgPmVfMrNhLtgjlmnZha2kOpuRiDw=
 github.com/go-stack/stack v1.8.1/go.mod h1:dcoOX6HbPZSZptuspn9bctJ+N/CnF5gGygcUP3XYfe4=
-github.com/go-task/slim-sprig/v3 v3.0.0 h1:sUs3vkvUymDpBKi3qH1YSqBQk9+9D/8M2mN1vB6EwHI=
-github.com/go-task/slim-sprig/v3 v3.0.0/go.mod h1:W848ghGpv3Qj3dhTPRyJypKRiqCdHZiAzKg9hl15HA8=
 github.com/go-test/deep v1.0.2-0.20181118220953-042da051cf31/go.mod h1:wGDj63lr65AM2AQyKZd/NYHGb0R+1RLqB8NKt3aSFNA=
 github.com/go-test/deep v1.0.2/go.mod h1:wGDj63lr65AM2AQyKZd/NYHGb0R+1RLqB8NKt3aSFNA=
 github.com/go-test/deep v1.1.1 h1:0r/53hagsehfO4bzD2Pgr/+RgHqhmf+k1Bpse2cTu1U=
 github.com/go-test/deep v1.1.1/go.mod h1:5C2ZWiW0ErCdrYzpqxLbTX7MG14M9iiw8DgHncVwcsE=
 github.com/go-yaml/yaml v2.1.0+incompatible/go.mod h1:w2MrLa16VYP0jy6N7M5kHaCkaLENm+P+Tv+MfurjSw0=
 github.com/goccy/go-json v0.10.4 h1:JSwxQzIqKfmFX1swYPpUThQZp/Ka4wzJdK0LWVytLPM=
 github.com/goccy/go-json v0.10.4/go.mod h1:oq7eo15ShAhp70Anwd5lgX2pLfOS3QCiwU/PULtXL6M=
-github.com/godbus/dbus/v5 v5.0.3/go.mod h1:xhWf0FNVPg57R7Z0UbKHbJfkEywrmjJnf7w5xrFpKfA=
 github.com/godbus/dbus/v5 v5.0.4/go.mod h1:xhWf0FNVPg57R7Z0UbKHbJfkEywrmjJnf7w5xrFpKfA=
 github.com/godbus/dbus/v5 v5.1.0 h1:4KLkAxT3aOY8Li4FRJe/KvhoNFFxo0m6fNuFUO8QJUk=
 github.com/godbus/dbus/v5 v5.1.0/go.mod h1:xhWf0FNVPg57R7Z0UbKHbJfkEywrmjJnf7w5xrFpKfA=
 github.com/gofrs/flock v0.8.1 h1:+gYjHKf32LDeiEEFhQaotPbLuUXjY5ZqxKgXy7n59aw=
 github.com/gofrs/flock v0.8.1/go.mod h1:F1TvTiK9OcQqauNUHlbJvyl9Qa1QvF/gOUDKA14jxHU=
 github.com/gogo/protobuf v1.1.1/go.mod h1:r8qH/GZQm5c6nD/R0oafs1akxWv10x8SbQlK7atdtwQ=
 github.com/gogo/protobuf v1.2.0/go.mod h1:r8qH/GZQm5c6nD/R0oafs1akxWv10x8SbQlK7atdtwQ=
-github.com/gogo/protobuf v1.3.1/go.mod h1:SlYgWuQ5SjCEi6WLHjHCa1yvBfUnHcTbrrZtXPKa29o=
 github.com/gogo/protobuf v1.3.2 h1:Ov1cvc58UF3b5XjBnZv7+opcTcQFZebYjWzi34vdm4Q=
 github.com/gogo/protobuf v1.3.2/go.mod h1:P1XiOD3dCwIKUDQYPy72D8LYyHL2YPYrpS2s69NZV8Q=
 github.com/golang-jwt/jwt v3.2.2+incompatible h1:IfV12K8xAKAnZqdXVzCZ+TOjboZ2keLg81eXfW3O+oY=
 github.com/golang-jwt/jwt v3.2.2+incompatible/go.mod h1:8pz2t5EyA70fFQQSrl6XZXzqecmYZeUEB8OUGHkxJ+I=
-github.com/golang-jwt/jwt/v4 v4.5.1 h1:JdqV9zKUdtaa9gdPlywC3aeoEsR681PlKC+4F5gQgeo=
-github.com/golang-jwt/jwt/v4 v4.5.1/go.mod h1:m21LjoU+eqJr34lmDMbreY2eSTRJ1cv77w39/MY0Ch0=
+github.com/golang-jwt/jwt/v4 v4.5.2 h1:YtQM7lnr8iZ+j5q71MGKkNw9Mn7AjHM68uc9g5fXeUI=
+github.com/golang-jwt/jwt/v4 v4.5.2/go.mod h1:m21LjoU+eqJr34lmDMbreY2eSTRJ1cv77w39/MY0Ch0=
 github.com/golang/glog v0.0.0-20160126235308-23def4e6c14b/go.mod h1:SBH7ygxi8pfUlaOkMMuAQtPIUF8ecWP5IEl/CR7VP2Q=
 github.com/golang/groupcache v0.0.0-20190702054246-869f871628b6/go.mod h1:cIg4eruTrX1D+g88fzRXU5OdNfaM+9IcxsU14FzY7Hc=
 github.com/golang/groupcache v0.0.0-20191227052852-215e87163ea7/go.mod h1:cIg4eruTrX1D+g88fzRXU5OdNfaM+9IcxsU14FzY7Hc=
 github.com/golang/groupcache v0.0.0-20200121045136-8c9f03a8e57e h1:1r7pUrabqp18hOBcwBwiTsbnFeTZHV9eER/QT5JVZxY=
 github.com/golang/groupcache v0.0.0-20200121045136-8c9f03a8e57e/go.mod h1:cIg4eruTrX1D+g88fzRXU5OdNfaM+9IcxsU14FzY7Hc=
-github.com/golang/lint v0.0.0-20180702182130-06c8688daad7/go.mod h1:tluoj9z5200jBnyusfRPU2LqT6J+DAorxEvtC7LHB+E=
 github.com/golang/mock v1.1.1/go.mod h1:oTYuIxOrZwtPieC+H1uAHpcLFnEyAGVDL/k47Jfbm0A=
 github.com/golang/mock v1.2.0/go.mod h1:oTYuIxOrZwtPieC+H1uAHpcLFnEyAGVDL/k47Jfbm0A=
 github.com/golang/mock v1.3.1/go.mod h1:sBzyDLLjw3U8JLTeZvSv8jJB+tU5PVekmnlKIyFUx0Y=
@@ -496,10 +458,9 @@ github.com/google/go-cmp v0.5.3/go.mod h1:v8dTdLbMG2kIc/vJvl+f65V22dbkXbowE6jgT/
 github.com/google/go-cmp v0.5.4/go.mod h1:v8dTdLbMG2kIc/vJvl+f65V22dbkXbowE6jgT/gNBxE=
 github.com/google/go-cmp v0.5.6/go.mod h1:v8dTdLbMG2kIc/vJvl+f65V22dbkXbowE6jgT/gNBxE=
 github.com/google/go-cmp v0.5.9/go.mod h1:17dUlkBOakJ0+DkrSSNjCkIjxS6bF9zb3elmeNGIjoY=
-github.com/google/go-cmp v0.6.0 h1:ofyhxvXcZhMsU5ulbFiLKl/XBFqE1GSq7atu8tAmTRI=
 github.com/google/go-cmp v0.6.0/go.mod h1:17dUlkBOakJ0+DkrSSNjCkIjxS6bF9zb3elmeNGIjoY=
-github.com/google/go-github v17.0.0+incompatible/go.mod h1:zLgOLi98H3fifZn+44m+umXrS52loVEgC2AApnigrVQ=
-github.com/google/go-querystring v1.0.0/go.mod h1:odCYkC5MyYFN7vkCjXpyrEuKhc/BUO6wN/zVPAxq5ck=
+github.com/google/go-cmp v0.7.0 h1:wk8382ETsv4JYUZwIsn6YpYiWiBsYLSJiTsyBybVuN8=
+github.com/google/go-cmp v0.7.0/go.mod h1:pXiqmnSA92OHEEa9HXL2W4E7lf9JzCmGVUdgjX3N/iU=
 github.com/google/gofuzz v1.0.0/go.mod h1:dBl0BpW6vV/+mYPU4Po3pmUjxk6FQPldtuIdl/M65Eg=
 github.com/google/gofuzz v1.2.0 h1:xRy4A+RhZaiKjJ1bPfwQ8sedCA+YS2YcCHW6ec7JMi0=
 github.com/google/gofuzz v1.2.0/go.mod h1:dBl0BpW6vV/+mYPU4Po3pmUjxk6FQPldtuIdl/M65Eg=
@@ -522,13 +483,10 @@ github.com/google/pprof v0.0.0-20230207041349-798e818bf904/go.mod h1:uglQLonpP8q
 github.com/google/pprof v0.0.0-20250317173921-a4b03ec1a45e h1:ijClszYn+mADRFY17kjQEVQ1XRhq2/JR1M3sGqeJoxs=
 github.com/google/pprof v0.0.0-20250317173921-a4b03ec1a45e/go.mod h1:boTsfXsheKC2y+lKOCMpSfarhxDeIzfZG1jqGcPl3cA=
 github.com/google/renameio v0.1.0/go.mod h1:KWCgfxg9yswjAJkECMjeO8J8rahYeXnNhOm40UhjYkI=
-github.com/google/subcommands v1.2.0/go.mod h1:ZjhPrFU+Olkh9WazFPsl27BQ4UPiG37m3yTrtFlrHVk=
 github.com/google/uuid v1.1.2/go.mod h1:TIyPZe4MgqvfeYDBFedMoGGpEw/LqOeaOT+nhxU+yHo=
 github.com/google/uuid v1.3.1/go.mod h1:TIyPZe4MgqvfeYDBFedMoGGpEw/LqOeaOT+nhxU+yHo=
 github.com/google/uuid v1.6.0 h1:NIvaJDMOsjHA8n1jAhLSgzrAzy1Hgr+hNrb57e+94F0=
 github.com/google/uuid v1.6.0/go.mod h1:TIyPZe4MgqvfeYDBFedMoGGpEw/LqOeaOT+nhxU+yHo=
-github.com/googleapis/gax-go v2.0.0+incompatible/go.mod h1:SFVmujtThgffbyetf+mdk2eWhX2bMyUtNHzFKcPA9HY=
-github.com/googleapis/gax-go/v2 v2.0.3/go.mod h1:LLvjysVCY1JZeum8Z6l8qUty8fiNwE08qbEPm1M08qg=
 github.com/googleapis/gax-go/v2 v2.0.4/go.mod h1:0Wqv26UfaUD9n4G6kQubkQ+KchISgw+vpHVxEJEs9eg=
 github.com/googleapis/gax-go/v2 v2.0.5/go.mod h1:DWXyrwAJ9X0FpwwEdw+IPEYBICEFu5mhpdKc/us6bOk=
 github.com/googleapis/google-cloud-go-testing v0.0.0-20200911160855-bcd43fbb19e8/go.mod h1:dvDLG8qkwmyD9a/MJJN3XJcT3xFxOKAvTZGvuZmac9g=
@@ -544,12 +502,10 @@ github.com/gorilla/websocket v1.5.3 h1:saDtZ6Pbx/0u+bgYQ3q96pZgCzfhKXGPqt7kZ72aN
 github.com/gorilla/websocket v1.5.3/go.mod h1:YR8l580nyteQvAITg2hZ9XVh4b55+EU/adAjf1fMHhE=
 github.com/graph-gophers/graphql-go v1.3.0 h1:Eb9x/q6MFpCLz7jBCiP/WTxjSDrYLR1QY41SORZyNJ0=
 github.com/graph-gophers/graphql-go v1.3.0/go.mod h1:9CQHMSxwO4MprSdzoIEobiHpoLtHm77vfxsvsIN5Vuc=
-github.com/gregjones/httpcache v0.0.0-20180305231024-9cad4c3443a7/go.mod h1:FecbI9+v66THATjSRHfNgh1IVFe/9kFxbXtjV0ctIMA=
 github.com/grpc-ecosystem/go-grpc-middleware v1.4.0 h1:UH//fgunKIs4JdUbpDl1VZCDaL56wXCB/5+wF6uHfaI=
 github.com/grpc-ecosystem/go-grpc-middleware v1.4.0/go.mod h1:g5qyo/la0ALbONm6Vbp88Yd8NsDy6rZz+RcrMPxvld8=
 github.com/grpc-ecosystem/go-grpc-prometheus v1.2.0 h1:Ovs26xHkKqVztRpIrF/92BcuyuQ/YW4NSIpoGtfXNho=
 github.com/grpc-ecosystem/go-grpc-prometheus v1.2.0/go.mod h1:8NvIoxWQoOIhqOTXgfV/d3M/q6VIi02HzZEHgUlZvzk=
-github.com/grpc-ecosystem/grpc-gateway v1.5.0/go.mod h1:RSKVYQBd5MCa4OVpNdGskqpgL2+G+NZTnrVHpWWfpdw=
 github.com/hashicorp/errwrap v1.0.0/go.mod h1:YH+1FKiLXxHSkmPseP+kNlulaMuP3n2brvKWEqk/Jc4=
 github.com/hashicorp/errwrap v1.1.0 h1:OxrOeh75EUXMY8TBjag2fzXGZ40LB6IKw45YeGUDY2I=
 github.com/hashicorp/errwrap v1.1.0/go.mod h1:YH+1FKiLXxHSkmPseP+kNlulaMuP3n2brvKWEqk/Jc4=
@@ -609,7 +565,6 @@ github.com/holiman/uint256 v1.3.2/go.mod h1:EOMSn4q6Nyt9P6efbI3bueV4e1b3dGlUCXei
 github.com/hpcloud/tail v1.0.0/go.mod h1:ab1qPbhIpdTxEkNHXyeSf5vhxWSCs/tWer42PpOxQnU=
 github.com/huandu/xstrings v1.0.0/go.mod h1:4qWG/gcEcfX4z/mBDHJ++3ReCw9ibxbsNJbcucJdbSo=
 github.com/huandu/xstrings v1.2.0/go.mod h1:DvyZB1rfVYsBIigL8HwpZgxHwXozlTgGqn63UyNX5k4=
-github.com/huandu/xstrings v1.3.0/go.mod h1:y5/lhBue+AyNmUVz9RLU9xbLR0o4KIIExikq4ovT0aE=
 github.com/huandu/xstrings v1.3.1/go.mod h1:y5/lhBue+AyNmUVz9RLU9xbLR0o4KIIExikq4ovT0aE=
 github.com/huandu/xstrings v1.3.2/go.mod h1:y5/lhBue+AyNmUVz9RLU9xbLR0o4KIIExikq4ovT0aE=
 github.com/huandu/xstrings v1.4.0 h1:D17IlohoQq4UcpqD7fDk80P7l+lwAmlFaBHgOipl2FU=
@@ -651,8 +606,8 @@ github.com/ipfs/go-block-format v0.2.0 h1:ZqrkxBA2ICbDRbK8KJs/u0O3dlp6gmAuuXUJNi
 github.com/ipfs/go-block-format v0.2.0/go.mod h1:+jpL11nFx5A/SPpsoBn6Bzkra/zaArfSmsknbPMYgzM=
 github.com/ipfs/go-cid v0.5.0 h1:goEKKhaGm0ul11IHA7I6p1GmKz8kEYniqFopaB5Otwg=
 github.com/ipfs/go-cid v0.5.0/go.mod h1:0L7vmeNXpQpUS9vt+yEARkJ8rOg43DF3iPgn4GIN0mk=
-github.com/ipfs/go-datastore v0.6.0 h1:JKyz+Gvz1QEZw0LsX1IBn+JFCJQH4SJVFtM4uWU0Myk=
-github.com/ipfs/go-datastore v0.6.0/go.mod h1:rt5M3nNbSO/8q1t4LNkLyUwRs8HupMeN/8O4Vn9YAT8=
+github.com/ipfs/go-datastore v0.8.2 h1:Jy3wjqQR6sg/LhyY0NIePZC3Vux19nLtg7dx0TVqr6U=
+github.com/ipfs/go-datastore v0.8.2/go.mod h1:W+pI1NsUsz3tcsAACMtfC+IZdnQTnC/7VfPoJBQuts0=
 github.com/ipfs/go-detect-race v0.0.1 h1:qX/xay2W3E4Q1U7d9lNs1sU9nvguX0a7319XbyQ6cOk=
 github.com/ipfs/go-detect-race v0.0.1/go.mod h1:8BNT7shDZPo99Q74BpGMK+4D8Mn4j46UU0LZ723meps=
 github.com/ipfs/go-ipfs-api v0.7.0 h1:CMBNCUl0b45coC+lQCXEVpMhwoqjiaCwUIrM+coYW2Q=
@@ -667,12 +622,8 @@ github.com/ipld/go-ipld-prime v0.21.0 h1:n4JmcpOlPDIxBcY037SVfpd1G+Sj1nKZah0m6QH
 github.com/ipld/go-ipld-prime v0.21.0/go.mod h1:3RLqy//ERg/y5oShXXdx5YIp50cFGOanyMctpPjsvxQ=
 github.com/jackpal/go-nat-pmp v1.0.2 h1:KzKSgb7qkJvOUTqYl9/Hg/me3pWgBmERKrTGD7BdWus=
 github.com/jackpal/go-nat-pmp v1.0.2/go.mod h1:QPH045xvCAeXUZOxsnwmrtiCoxIr9eob+4orBN1SBKc=
-github.com/jbenet/go-cienv v0.1.0/go.mod h1:TqNnHUmJgXau0nCzC7kXWeotg3J9W34CUv5Djy1+FlA=
 github.com/jbenet/go-temp-err-catcher v0.1.0 h1:zpb3ZH6wIE8Shj2sKS+khgRvf7T7RABoLk/+KKHggpk=
 github.com/jbenet/go-temp-err-catcher v0.1.0/go.mod h1:0kJRvmDZXNMIiJirNPEYfhpPwbGVtZVWC34vc5WLsDk=
-github.com/jbenet/goprocess v0.1.4 h1:DRGOFReOMqqDNXwW70QkacFW0YN9QnwLV0Vqk+3oU0o=
-github.com/jbenet/goprocess v0.1.4/go.mod h1:5yspPrukOVuOLORacaBi858NqyClJPQxYZlqdZVfqY4=
-github.com/jellevandenhooff/dkim v0.0.0-20150330215556-f50fe3d243e1/go.mod h1:E0B/fFc00Y+Rasa88328GlI/XbtyysCtTHZS8h7IrBU=
 github.com/jessevdk/go-flags v0.0.0-20141203071132-1679536dcc89/go.mod h1:4FA24M0QyGHXBuZZK/XkWh8h0e1EYbRYJSGM75WSRxI=
 github.com/jessevdk/go-flags v1.4.0/go.mod h1:4FA24M0QyGHXBuZZK/XkWh8h0e1EYbRYJSGM75WSRxI=
 github.com/jmespath/go-jmespath v0.0.0-20180206201540-c2b33e8439af/go.mod h1:Nht3zPeWKUH0NzdCt2Blrr5ys8VGpn0CEB0cQHVjt7k=
@@ -687,27 +638,24 @@ github.com/jtolds/gls v4.2.1+incompatible/go.mod h1:QJZ7F/aHp+rZTRtaJ1ow/lLfFfVY
 github.com/jtolds/gls v4.20.0+incompatible h1:xdiiI2gbIgH/gLH7ADydsJ1uDOEzR8yvV7C0MuV77Wo=
 github.com/jtolds/gls v4.20.0+incompatible/go.mod h1:QJZ7F/aHp+rZTRtaJ1ow/lLfFfVYBRgL+9YlvaHOwJU=
 github.com/julienschmidt/httprouter v1.2.0/go.mod h1:SYymIcj16QtmaHHD7aYtjjsJG7VTCxuUUipMqKk8s4w=
-github.com/kisielk/errcheck v1.2.0/go.mod h1:/BMXB+zMLi60iA8Vv6Ksmxu/1UDYcXs4uQLJ+jE2L00=
 github.com/kisielk/errcheck v1.5.0/go.mod h1:pFxgyoBC7bSaBwPgfKdkLd5X25qrDl4LWUI2bnpBCr8=
 github.com/kisielk/gotool v1.0.0/go.mod h1:XhKaO+MFFWcvkIS/tQcRk01m1F5IRFswLeQ+oQHNcck=
 github.com/kkdai/bstream v0.0.0-20161212061736-f391b8402d23/go.mod h1:J+Gs4SYgM6CZQHDETBtE9HaSEkGmuNXF86RwHhHUvq4=
-github.com/klauspost/compress v1.17.11 h1:In6xLpyWOi1+C7tXUUWv2ot1QvBjxevKAaI6IXrJmUc=
-github.com/klauspost/compress v1.17.11/go.mod h1:pMDklpSncoRMuLFrf1W9Ss9KT+0rH90U12bZKk7uwG0=
-github.com/klauspost/cpuid/v2 v2.2.9 h1:66ze0taIn2H33fBvCkXuv9BmCwDfafmiIVpKV9kKGuY=
-github.com/klauspost/cpuid/v2 v2.2.9/go.mod h1:rqkxqrZ1EhYM9G+hXH7YdowN5R5RGN6NK4QwQ3WMXF8=
+github.com/klauspost/compress v1.18.0 h1:c/Cqfb0r+Yi+JtIEq73FWXVkRonBlf0CRNYc8Zttxdo=
+github.com/klauspost/compress v1.18.0/go.mod h1:2Pp+KzxcywXVXMr50+X0Q/Lsb43OQHYWRCY2AiWywWQ=
+github.com/klauspost/cpuid/v2 v2.2.10 h1:tBs3QSyvjDyFTq3uoc/9xFpCuOsJQFNPiAhYdw2skhE=
+github.com/klauspost/cpuid/v2 v2.2.10/go.mod h1:hqwkgyIinND0mEev00jJYCxPNVRVXFQeu1XKlok6oO0=
 github.com/konsorten/go-windows-terminal-sequences v1.0.1/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
-github.com/koron/go-ssdp v0.0.5 h1:E1iSMxIs4WqxTbIBLtmNBeOOC+1sCIXQeqTWVnpmwhk=
-github.com/koron/go-ssdp v0.0.5/go.mod h1:Qm59B7hpKpDqfyRNWRNr00jGwLdXjDyZh6y7rH6VS0w=
+github.com/koron/go-ssdp v0.0.6 h1:Jb0h04599eq/CY7rB5YEqPS83HmRfHP2azkxMN2rFtU=
+github.com/koron/go-ssdp v0.0.6/go.mod h1:0R9LfRJGek1zWTjN3JUNlm5INCDYGpRDfAptnct63fI=
 github.com/kr/fs v0.1.0/go.mod h1:FFnZGqtBN9Gxj7eW1uZ42v5BccTP0vu6NEaFoC2HwRg=
 github.com/kr/logfmt v0.0.0-20140226030751-b84e30acd515/go.mod h1:+0opPa2QZZtGFBFZlji/RkVcI2GknAs/DXo4wKdlNEc=
 github.com/kr/pretty v0.1.0/go.mod h1:dAy3ld7l9f0ibDNOQOHHMYYIIbhfbHSm3C4ZsoJORNo=
-github.com/kr/pretty v0.2.0/go.mod h1:ipq/a2n7PKx3OHsz4KJII5eveXtPO4qwEXGdVfWzfnI=
 github.com/kr/pretty v0.2.1/go.mod h1:ipq/a2n7PKx3OHsz4KJII5eveXtPO4qwEXGdVfWzfnI=
 github.com/kr/pretty v0.3.0/go.mod h1:640gp4NfQd8pI5XOwp5fnNeVWj67G7CFk/SaSQn7NBk=
 github.com/kr/pretty v0.3.1 h1:flRD4NNwYAUpkphVc1HcthR4KEIFJ65n8Mw5qdRn3LE=
 github.com/kr/pretty v0.3.1/go.mod h1:hoEshYVHaxMs3cyo3Yncou5ZscifuDolrwPKZanG3xk=
 github.com/kr/pty v1.1.1/go.mod h1:pFQYn66WHrOpPYNljwOMqo10TkYh1fy3cYio2l3bCsQ=
-github.com/kr/pty v1.1.3/go.mod h1:pFQYn66WHrOpPYNljwOMqo10TkYh1fy3cYio2l3bCsQ=
 github.com/kr/text v0.1.0/go.mod h1:4Jbv+DJW3UT/LiOwJeYQe1efqtUx/iVham/4vfdArNI=
 github.com/kr/text v0.2.0 h1:5Nx0Ya0ZqY2ygV366QzturHI13Jq95ApcVaJBhpS+AY=
 github.com/kr/text v0.2.0/go.mod h1:eLer722TekiGuMkidMxC/pM04lWEeraHUUmBw8l2grE=
@@ -723,8 +671,8 @@ github.com/libp2p/go-cidranger v1.1.0 h1:ewPN8EZ0dd1LSnrtuwd4709PXVcITVeuwbag38y
 github.com/libp2p/go-cidranger v1.1.0/go.mod h1:KWZTfSr+r9qEo9OkI9/SIEeAtw+NNoU0dXIXt15Okic=
 github.com/libp2p/go-flow-metrics v0.2.0 h1:EIZzjmeOE6c8Dav0sNv35vhZxATIXWZg6j/C08XmmDw=
 github.com/libp2p/go-flow-metrics v0.2.0/go.mod h1:st3qqfu8+pMfh+9Mzqb2GTiwrAGjIPszEjZmtksN8Jc=
-github.com/libp2p/go-libp2p v0.39.0 h1:LmrhDRud4eDkQCSB4l5NfoIFDqvDwAyANmfeYkgnKgs=
-github.com/libp2p/go-libp2p v0.39.0/go.mod h1:3zicI8Lp7Isun+Afo/JOACUbbJqqR2owK6RQWFsVAbI=
+github.com/libp2p/go-libp2p v0.46.0 h1:0T2yvIKpZ3DVYCuPOFxPD1layhRU486pj9rSlGWYnDM=
+github.com/libp2p/go-libp2p v0.46.0/go.mod h1:TbIDnpDjBLa7isdgYpbxozIVPBTmM/7qKOJP4SFySrQ=
 github.com/libp2p/go-libp2p-asn-util v0.4.1 h1:xqL7++IKD9TBFMgnLPZR6/6iYhawHKHl950SO9L6n94=
 github.com/libp2p/go-libp2p-asn-util v0.4.1/go.mod h1:d/NI6XZ9qxw67b4e+NgpQexCIiFYJjErASrYW4PFDN8=
 github.com/libp2p/go-libp2p-kad-dht v0.29.0 h1:045eW21lGlMSD9aKSZZGH4fnBMIInPwQLxIQ35P962I=
@@ -741,22 +689,20 @@ github.com/libp2p/go-libp2p-testing v0.12.0 h1:EPvBb4kKMWO29qP4mZGyhVzUyR25dvfUI
 github.com/libp2p/go-libp2p-testing v0.12.0/go.mod h1:KcGDRXyN7sQCllucn1cOOS+Dmm7ujhfEyXQL5lvkcPg=
 github.com/libp2p/go-msgio v0.3.0 h1:mf3Z8B1xcFN314sWX+2vOTShIE0Mmn2TXn3YCUQGNj0=
 github.com/libp2p/go-msgio v0.3.0/go.mod h1:nyRM819GmVaF9LX3l03RMh10QdOroF++NBbxAb0mmDM=
-github.com/libp2p/go-nat v0.2.0 h1:Tyz+bUFAYqGyJ/ppPPymMGbIgNRH+WqC5QrT5fKrrGk=
-github.com/libp2p/go-nat v0.2.0/go.mod h1:3MJr+GRpRkyT65EpVPBstXLvOlAPzUVlG6Pwg9ohLJk=
-github.com/libp2p/go-netroute v0.2.2 h1:Dejd8cQ47Qx2kRABg6lPwknU7+nBnFRpko45/fFPuZ8=
-github.com/libp2p/go-netroute v0.2.2/go.mod h1:Rntq6jUAH0l9Gg17w5bFGhcC9a+vk4KNXs6s7IljKYE=
+github.com/libp2p/go-netroute v0.3.0 h1:nqPCXHmeNmgTJnktosJ/sIef9hvwYCrsLxXmfNks/oc=
+github.com/libp2p/go-netroute v0.3.0/go.mod h1:Nkd5ShYgSMS5MUKy/MU2T57xFoOKvvLR92Lic48LEyA=
 github.com/libp2p/go-reuseport v0.4.0 h1:nR5KU7hD0WxXCJbmw7r2rhRYruNRl2koHw8fQscQm2s=
 github.com/libp2p/go-reuseport v0.4.0/go.mod h1:ZtI03j/wO5hZVDFo2jKywN6bYKWLOy8Se6DrI2E1cLU=
-github.com/libp2p/go-yamux/v4 v4.0.2 h1:nrLh89LN/LEiqcFiqdKDRHjGstN300C1269K/EX0CPU=
-github.com/libp2p/go-yamux/v4 v4.0.2/go.mod h1:C808cCRgOs1iBwY4S71T5oxgMxgLmqUw56qh4AeBW2o=
+github.com/libp2p/go-yamux/v5 v5.0.1 h1:f0WoX/bEF2E8SbE4c/k1Mo+/9z0O4oC/hWEA+nfYRSg=
+github.com/libp2p/go-yamux/v5 v5.0.1/go.mod h1:en+3cdX51U0ZslwRdRLrvQsdayFt3TSUKvBGErzpWbU=
 github.com/lufia/plan9stats v0.0.0-20211012122336-39d0f177ccd0 h1:6E+4a0GO5zZEnZ81pIr0yLvtUWk2if982qA3F3QD6H4=
 github.com/lufia/plan9stats v0.0.0-20211012122336-39d0f177ccd0/go.mod h1:zJYVVT2jmtg6P3p1VtQj7WsuWi/y4VnjVBn7F8KPB3I=
-github.com/lunixbochs/vtclean v1.0.0/go.mod h1:pHhQNgMf3btfWnGBVipUOjRYhoOsdGqdm/+2c2E2WMI=
 github.com/mackerelio/go-osstat v0.2.4 h1:qxGbdPkFo65PXOb/F/nhDKpF2nGmGaCFDLXoZjJTtUs=
 github.com/mackerelio/go-osstat v0.2.4/go.mod h1:Zy+qzGdZs3A9cuIqmgbJvwbmLQH9dJvtio5ZjJTbdlQ=
 github.com/magefile/mage v1.9.0 h1:t3AU2wNwehMCW97vuqQLtw6puppWXHO+O2MHo5a50XE=
 github.com/magefile/mage v1.9.0/go.mod h1:z5UZb/iS3GoOSn0JgWuiw7dxlurVYTu+/jHXqQg881A=
-github.com/mailru/easyjson v0.0.0-20190312143242-1de009706dbe/go.mod h1:C1wdFJiN94OJF2b5HbByQZoLdCWB1Yqtg26g4irojpc=
+github.com/marcopolo/simnet v0.0.1 h1:rSMslhPz6q9IvJeFWDoMGxMIrlsbXau3NkuIXHGJxfg=
+github.com/marcopolo/simnet v0.0.1/go.mod h1:WDaQkgLAjqDUEBAOXz22+1j6wXKfGlC5sD5XWt3ddOs=
 github.com/marten-seemann/tcp v0.0.0-20210406111302-dfbc87cc63fd h1:br0buuQ854V8u83wA0rVZ8ttrq5CpaPZdvrK0LP2lOk=
 github.com/marten-seemann/tcp v0.0.0-20210406111302-dfbc87cc63fd/go.mod h1:QuCEs1Nt24+FYQEqAAncTDPJIuGs+LxK1MCiFL25pMU=
 github.com/maticnetwork/crand v1.0.2 h1:Af0tAivC8zrxXDpGWNWVT/0s1fOz8w0eRbahZgURS8I=
@@ -776,9 +722,8 @@ github.com/mattn/go-runewidth v0.0.9/go.mod h1:H031xJmbD/WCDINGzjvQ9THkh0rPKHF+m
 github.com/mattn/go-runewidth v0.0.15 h1:UNAjwbU9l54TA3KzvqLGxwWjHmMgBUVhBiTjelZgg3U=
 github.com/mattn/go-runewidth v0.0.15/go.mod h1:Jdepj2loyihRzMpdS35Xk/zdY8IAYHsh153qUoGf23w=
 github.com/matttproud/golang_protobuf_extensions v1.0.1/go.mod h1:D8He9yQNgCq6Z5Ld7szi9bcBfOoFv/3dc6xSMkL2PC0=
-github.com/microcosm-cc/bluemonday v1.0.1/go.mod h1:hsXNsILzKxV+sX77C5b8FSuKF00vh2OMYv+xgHpAMF4=
-github.com/miekg/dns v1.1.63 h1:8M5aAw6OMZfFXTT7K5V0Eu5YiiL8l7nUAkyN6C9YwaY=
-github.com/miekg/dns v1.1.63/go.mod h1:6NGHfjhpmr5lt3XPLuyfDJi5AXbNIPM9PY6H6sF1Nfs=
+github.com/miekg/dns v1.1.66 h1:FeZXOS3VCVsKnEAd+wBkjMC3D2K+ww66Cq3VnCINuJE=
+github.com/miekg/dns v1.1.66/go.mod h1:jGFzBsSNbJw6z1HYut1RKBKHA9PBdxeHrZG8J+gC2WE=
 github.com/mikioh/tcp v0.0.0-20190314235350-803a9b46060c h1:bzE/A84HN25pxAuk9Eej1Kz9OUelF97nAc82bDquQI8=
 github.com/mikioh/tcp v0.0.0-20190314235350-803a9b46060c/go.mod h1:0SQS9kMwD2VsyFEB++InYyBJroV/FRmBgcydeSUcJms=
 github.com/mikioh/tcpinfo v0.0.0-20190314235526-30a79bb1804b h1:z78hV3sbSMAUoyUMM0I83AUIT6Hu17AWfgjzIbtrYFc=
@@ -806,9 +751,6 @@ github.com/mitchellh/mapstructure v1.5.0/go.mod h1:bFUtVrKA4DC2yAKiSyO/QUcy7e+RR
 github.com/mitchellh/pointerstructure v1.2.0 h1:O+i9nHnXS3l/9Wu7r4NrEdwA2VFTicjUEN1uBnDo34A=
 github.com/mitchellh/pointerstructure v1.2.0/go.mod h1:BRAsLI5zgXmw97Lf6s25bs8ohIXc3tViBH44KcwB2g4=
 github.com/mitchellh/reflectwalk v1.0.0/go.mod h1:mSTlrgnPZtwu0c4WaC2kGObEpuNDbx0jmZXqmk4esnw=
-github.com/mmcloughlin/addchain v0.4.0 h1:SobOdjm2xLj1KkXN5/n0xTIWyZA2+s99UCY1iPfkHRY=
-github.com/mmcloughlin/addchain v0.4.0/go.mod h1:A86O+tHqZLMNO4w6ZZ4FlVQEadcoqkyU72HC5wJ4RlU=
-github.com/mmcloughlin/profile v0.1.1/go.mod h1:IhHD7q1ooxgwTgjxQYkACGA77oFTDdFVejUS1/tS/qU=
 github.com/modern-go/concurrent v0.0.0-20180228061459-e0a39a4cb421/go.mod h1:6dJC0mAP4ikYIbvyc7fijjWJddQyLn8Ig3JB5CqoB9Q=
 github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd h1:TRLaZ9cD/w8PVh93nsPXa1VrQ6jlwL5oN8l14QlcNfg=
 github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd/go.mod h1:6dJC0mAP4ikYIbvyc7fijjWJddQyLn8Ig3JB5CqoB9Q=
@@ -829,30 +771,28 @@ github.com/multiformats/go-base32 v0.1.0/go.mod h1:Kj3tFY6zNr+ABYMqeUNeGvkIC/UYg
 github.com/multiformats/go-base36 v0.2.0 h1:lFsAbNOGeKtuKozrtBsAkSVhv1p9D0/qedU9rQyccr0=
 github.com/multiformats/go-base36 v0.2.0/go.mod h1:qvnKE++v+2MWCfePClUEjE78Z7P2a1UV0xHgWc0hkp4=
 github.com/multiformats/go-multiaddr v0.1.1/go.mod h1:aMKBKNEYmzmDmxfX88/vz+J5IU55txyt0p4aiWVohjo=
-github.com/multiformats/go-multiaddr v0.14.0 h1:bfrHrJhrRuh/NXH5mCnemjpbGjzRw/b+tJFOD41g2tU=
-github.com/multiformats/go-multiaddr v0.14.0/go.mod h1:6EkVAxtznq2yC3QT5CM1UTAwG0GTP3EWAIcjHuzQ+r4=
+github.com/multiformats/go-multiaddr v0.16.0 h1:oGWEVKioVQcdIOBlYM8BH1rZDWOGJSqr9/BKl6zQ4qc=
+github.com/multiformats/go-multiaddr v0.16.0/go.mod h1:JSVUmXDjsVFiW7RjIFMP7+Ev+h1DTbiJgVeTV/tcmP0=
 github.com/multiformats/go-multiaddr-dns v0.4.1 h1:whi/uCLbDS3mSEUMb1MsoT4uzUeZB0N32yzufqS0i5M=
 github.com/multiformats/go-multiaddr-dns v0.4.1/go.mod h1:7hfthtB4E4pQwirrz+J0CcDUfbWzTqEzVyYKKIKpgkc=
 github.com/multiformats/go-multiaddr-fmt v0.1.0 h1:WLEFClPycPkp4fnIzoFoV9FVd49/eQsuaL3/CWe167E=
 github.com/multiformats/go-multiaddr-fmt v0.1.0/go.mod h1:hGtDIW4PU4BqJ50gW2quDuPVjyWNZxToGUh/HwTZYJo=
 github.com/multiformats/go-multibase v0.2.0 h1:isdYCVLvksgWlMW9OZRYJEa9pZETFivncJHmHnnd87g=
 github.com/multiformats/go-multibase v0.2.0/go.mod h1:bFBZX4lKCA/2lyOFSAoKH5SS6oPyjtnzK/XTFDPkNuk=
-github.com/multiformats/go-multicodec v0.9.0 h1:pb/dlPnzee/Sxv/j4PmkDRxCOi3hXTz3IbPKOXWJkmg=
-github.com/multiformats/go-multicodec v0.9.0/go.mod h1:L3QTQvMIaVBkXOXXtVmYE+LI16i14xuaojr/H7Ai54k=
+github.com/multiformats/go-multicodec v0.9.1 h1:x/Fuxr7ZuR4jJV4Os5g444F7xC4XmyUaT/FWtE+9Zjo=
+github.com/multiformats/go-multicodec v0.9.1/go.mod h1:LLWNMtyV5ithSBUo3vFIMaeDy+h3EbkMTek1m+Fybbo=
 github.com/multiformats/go-multihash v0.0.8/go.mod h1:YSLudS+Pi8NHE7o6tb3D8vrpKa63epEDmG8nTduyAew=
 github.com/multiformats/go-multihash v0.2.3 h1:7Lyc8XfX/IY2jWb/gI7JP+o7JEq9hOa7BFvVU9RSh+U=
 github.com/multiformats/go-multihash v0.2.3/go.mod h1:dXgKXCXjBzdscBLk9JkjINiEsCKRVch90MdaGiKsvSM=
-github.com/multiformats/go-multistream v0.6.0 h1:ZaHKbsL404720283o4c/IHQXiS6gb8qAN5EIJ4PN5EA=
-github.com/multiformats/go-multistream v0.6.0/go.mod h1:MOyoG5otO24cHIg8kf9QW2/NozURlkP/rvi2FQJyCPg=
+github.com/multiformats/go-multistream v0.6.1 h1:4aoX5v6T+yWmc2raBHsTvzmFhOI8WVOer28DeBBEYdQ=
+github.com/multiformats/go-multistream v0.6.1/go.mod h1:ksQf6kqHAb6zIsyw7Zm+gAuVo57Qbq84E27YlYqavqw=
 github.com/multiformats/go-varint v0.0.7 h1:sWSGR+f/eu5ABZA2ZpYKBILXTTs9JWpdEM/nEGOHFS8=
 github.com/multiformats/go-varint v0.0.7/go.mod h1:r8PUYw/fD/SjBCiKOoDlGF6QawOELpZAu9eioSos/OU=
 github.com/munnerz/goautoneg v0.0.0-20191010083416-a7dc8b61c822 h1:C3w9PqII01/Oq1c1nUAm88MOHcQC9l5mIlSMApZMrHA=
 github.com/munnerz/goautoneg v0.0.0-20191010083416-a7dc8b61c822/go.mod h1:+n7T8mK8HuQTcFwEeznm/DIxMOiR9yIdICNftLE1DvQ=
 github.com/mwitkow/go-conntrack v0.0.0-20161129095857-cc309e4a2223/go.mod h1:qRWi+5nqEBWmkhHvq77mSJWrCKwh8bxhgT7d/eI7P4U=
 github.com/ncruces/go-strftime v0.1.9 h1:bY0MQC28UADQmHmaF5dgpLmImcShSi2kHU9XLdhx/f4=
 github.com/ncruces/go-strftime v0.1.9/go.mod h1:Fwc5htZGVVkseilnfgOVb9mKy6w1naJmn9CehxcKcls=
-github.com/neelance/astrewrite v0.0.0-20160511093645-99348263ae86/go.mod h1:kHJEU3ofeGjhHklVoIGuVj85JJwZ6kWPaJwCIxgnFmo=
-github.com/neelance/sourcemap v0.0.0-20151028013722-8c68805598ab/go.mod h1:Qr6/a/Q4r9LP1IltGz7tA7iOK1WonHEYhu1HRBA7ZiM=
 github.com/nxadm/tail v1.4.4/go.mod h1:kenIhsEOeOJmVchQTgglprH7qJGnHDVpk1VPCcaMI8A=
 github.com/nxadm/tail v1.4.11 h1:8feyoE3OzPrcshW5/MJ4sGESc5cqmGkGCWlco4l0bqY=
 github.com/nxadm/tail v1.4.11/go.mod h1:OTaG3NK980DZzxbRq6lEuzgU+mug70nY11sMd4JXXHc=
@@ -865,21 +805,17 @@ github.com/onsi/ginkgo v1.12.1/go.mod h1:zj2OWP4+oCPe1qIXoGWkgMRwljMUYCdkwsT2108
 github.com/onsi/ginkgo v1.14.0/go.mod h1:iSB4RoI2tjJc9BBv4NKIKWKya62Rps+oPG/Lv9klQyY=
 github.com/onsi/ginkgo v1.16.5 h1:8xi0RTUf59SOSfEtZMvwTvXYMzG4gV23XVHOZiXNtnE=
 github.com/onsi/ginkgo v1.16.5/go.mod h1:+E8gABHa3K6zRBolWtd+ROzc/U5bkGt0FwiG042wbpU=
-github.com/onsi/ginkgo/v2 v2.22.2 h1:/3X8Panh8/WwhU/3Ssa6rCKqPLuAkVY2I0RoyDLySlU=
-github.com/onsi/ginkgo/v2 v2.22.2/go.mod h1:oeMosUL+8LtarXBHu/c0bx2D/K9zyQ6uX3cTyztHwsk=
 github.com/onsi/gomega v1.4.1/go.mod h1:C1qb7wdrVGGVU+Z6iS04AVkA3Q65CEZX59MT0QO5uiA=
 github.com/onsi/gomega v1.4.3/go.mod h1:ex+gbHU/CVuBBDIJjb2X0qEXbFg53c61hWP/1CpauHY=
 github.com/onsi/gomega v1.7.1/go.mod h1:XdKZgCCFLUoM/7CFJVPcG8C1xQ1AJ0vpAezJrB7JYyY=
 github.com/onsi/gomega v1.10.1/go.mod h1:iN09h71vgCQne3DLsj+A5owkum+a2tYe+TOCB1ybHNo=
 github.com/onsi/gomega v1.36.2 h1:koNYke6TVk6ZmnyHrCXba/T/MoLBXFjeC1PtvYgw0A8=
 github.com/onsi/gomega v1.36.2/go.mod h1:DdwyADRjrc825LhMEkD76cHR5+pUnjhUN8GlHlRPHzY=
-github.com/opencontainers/runtime-spec v1.0.2/go.mod h1:jwyrGlmzljRJv/Fgzds9SsS/C5hL+LL3ko9hs6T5lQ0=
 github.com/opencontainers/runtime-spec v1.2.0 h1:z97+pHb3uELt/yiAWD691HNHQIF07bE7dzrbT927iTk=
 github.com/opencontainers/runtime-spec v1.2.0/go.mod h1:jwyrGlmzljRJv/Fgzds9SsS/C5hL+LL3ko9hs6T5lQ0=
 github.com/opentracing/opentracing-go v1.1.0/go.mod h1:UkNAQd3GIcIGf0SeVgPpRdFStlNbqXla1AfSYxPUl2o=
 github.com/opentracing/opentracing-go v1.2.0 h1:uEJPy/1a5RIPAJ0Ov+OIO8OxWu77jEv+1B0VhjKrZUs=
 github.com/opentracing/opentracing-go v1.2.0/go.mod h1:GxEUsuufX4nBwe+T+Wl9TAgYrxe9dPLANfrWvHYVTgc=
-github.com/openzipkin/zipkin-go v0.1.1/go.mod h1:NtoC/o8u3JlF1lSlyPNswIbeQH9bJTmOf0Erfk+hxe8=
 github.com/openzipkin/zipkin-go v0.1.6/go.mod h1:QgAqvLzwWbR/WpD4A3cGpPtJrZXNIiJc5AZX7/PBEpw=
 github.com/pascaldekloe/goe v0.1.0/go.mod h1:lzWF7FIEvWOWxwDKqyGYQf6ZUaNfKdP144TG7ZOy1lc=
 github.com/pbnjay/memory v0.0.0-20210728143218-7b4eea64cf58 h1:onHthvaw9LFnH4t2DcNVpwGmV9E1BkGknEliJkfwQj0=
@@ -900,14 +836,14 @@ github.com/pion/datachannel v1.5.10/go.mod h1:p/jJfC9arb29W7WrxyKbepTU20CFgyx5oL
 github.com/pion/dtls/v2 v2.2.7/go.mod h1:8WiMkebSHFD0T+dIU+UeBaoV7kDhOW5oDCzZ7WZ/F9s=
 github.com/pion/dtls/v2 v2.2.12 h1:KP7H5/c1EiVAAKUmXyCzPiQe5+bCJrpOeKg/L05dunk=
 github.com/pion/dtls/v2 v2.2.12/go.mod h1:d9SYc9fch0CqK90mRk1dC7AkzzpwJj6u2GU3u+9pqFE=
-github.com/pion/dtls/v3 v3.0.4 h1:44CZekewMzfrn9pmGrj5BNnTMDCFwr+6sLH+cCuLM7U=
-github.com/pion/dtls/v3 v3.0.4/go.mod h1:R373CsjxWqNPf6MEkfdy3aSe9niZvL/JaKlGeFphtMg=
+github.com/pion/dtls/v3 v3.0.6 h1:7Hkd8WhAJNbRgq9RgdNh1aaWlZlGpYTzdqjy9x9sK2E=
+github.com/pion/dtls/v3 v3.0.6/go.mod h1:iJxNQ3Uhn1NZWOMWlLxEEHAN5yX7GyPvvKw04v9bzYU=
 github.com/pion/ice/v2 v2.3.37 h1:ObIdaNDu1rCo7hObhs34YSBcO7fjslJMZV0ux+uZWh0=
 github.com/pion/ice/v2 v2.3.37/go.mod h1:mBF7lnigdqgtB+YHkaY/Y6s6tsyRyo4u4rPGRuOjUBQ=
-github.com/pion/ice/v4 v4.0.6 h1:jmM9HwI9lfetQV/39uD0nY4y++XZNPhvzIPCb8EwxUM=
-github.com/pion/ice/v4 v4.0.6/go.mod h1:y3M18aPhIxLlcO/4dn9X8LzLLSma84cx6emMSu14FGw=
-github.com/pion/interceptor v0.1.37 h1:aRA8Zpab/wE7/c0O3fh1PqY0AJI3fCSEM5lRWJVorwI=
-github.com/pion/interceptor v0.1.37/go.mod h1:JzxbJ4umVTlZAf+/utHzNesY8tmRkM2lVmkS82TTj8Y=
+github.com/pion/ice/v4 v4.0.10 h1:P59w1iauC/wPk9PdY8Vjl4fOFL5B+USq1+xbDcN6gT4=
+github.com/pion/ice/v4 v4.0.10/go.mod h1:y3M18aPhIxLlcO/4dn9X8LzLLSma84cx6emMSu14FGw=
+github.com/pion/interceptor v0.1.40 h1:e0BjnPcGpr2CFQgKhrQisBU7V3GXK6wrfYrGYaU6Jq4=
+github.com/pion/interceptor v0.1.40/go.mod h1:Z6kqH7M/FYirg3frjGJ21VLSRJGBXB/KqaTIrdqnOic=
 github.com/pion/logging v0.2.2/go.mod h1:k0/tDVsRCX2Mb2ZEmTqNa7CWsQPc+YYCB7Q+5pahoms=
 github.com/pion/logging v0.2.3 h1:gHuf0zpoh1GW67Nr6Gj4cv5Z9ZscU7g/EaoC/Ke/igI=
 github.com/pion/logging v0.2.3/go.mod h1:z8YfknkquMe1csOrxK5kc+5/ZPAzMxbKLX5aXpbpC90=
@@ -921,16 +857,16 @@ github.com/pion/rtcp v1.2.12/go.mod h1:sn6qjxvnwyAkkPzPULIbVqSKI5Dv54Rv7VG0kNxh9
 github.com/pion/rtcp v1.2.15 h1:LZQi2JbdipLOj4eBjK4wlVoQWfrZbh3Q6eHtWtJBZBo=
 github.com/pion/rtcp v1.2.15/go.mod h1:jlGuAjHMEXwMUHK78RgX0UmEJFV4zUKOFHR7OP+D3D0=
 github.com/pion/rtp v1.8.3/go.mod h1:pBGHaFt/yW7bf1jjWAoUjpSNoDnw98KTMg+jWWvziqU=
-github.com/pion/rtp v1.8.11 h1:17xjnY5WO5hgO6SD3/NTIUPvSFw/PbLsIJyz1r1yNIk=
-github.com/pion/rtp v1.8.11/go.mod h1:8uMBJj32Pa1wwx8Fuv/AsFhn8jsgw+3rUC2PfoBZ8p4=
-github.com/pion/sctp v1.8.35 h1:qwtKvNK1Wc5tHMIYgTDJhfZk7vATGVHhXbUDfHbYwzA=
-github.com/pion/sctp v1.8.35/go.mod h1:EcXP8zCYVTRy3W9xtOF7wJm1L1aXfKRQzaM33SjQlzg=
-github.com/pion/sdp/v3 v3.0.10 h1:6MChLE/1xYB+CjumMw+gZ9ufp2DPApuVSnDT8t5MIgA=
-github.com/pion/sdp/v3 v3.0.10/go.mod h1:88GMahN5xnScv1hIMTqLdu/cOcUkj6a9ytbncwMCq2E=
+github.com/pion/rtp v1.8.19 h1:jhdO/3XhL/aKm/wARFVmvTfq0lC/CvN1xwYKmduly3c=
+github.com/pion/rtp v1.8.19/go.mod h1:bAu2UFKScgzyFqvUKmbvzSdPr+NGbZtv6UB2hesqXBk=
+github.com/pion/sctp v1.8.39 h1:PJma40vRHa3UTO3C4MyeJDQ+KIobVYRZQZ0Nt7SjQnE=
+github.com/pion/sctp v1.8.39/go.mod h1:cNiLdchXra8fHQwmIoqw0MbLLMs+f7uQ+dGMG2gWebE=
+github.com/pion/sdp/v3 v3.0.13 h1:uN3SS2b+QDZnWXgdr69SM8KB4EbcnPnPf2Laxhty/l4=
+github.com/pion/sdp/v3 v3.0.13/go.mod h1:88GMahN5xnScv1hIMTqLdu/cOcUkj6a9ytbncwMCq2E=
 github.com/pion/srtp/v2 v2.0.20 h1:HNNny4s+OUmG280ETrCdgFndp4ufx3/uy85EawYEhTk=
 github.com/pion/srtp/v2 v2.0.20/go.mod h1:0KJQjA99A6/a0DOVTu1PhDSw0CXF2jTkqOoMg3ODqdA=
-github.com/pion/srtp/v3 v3.0.4 h1:2Z6vDVxzrX3UHEgrUyIGM4rRouoC7v+NiF1IHtp9B5M=
-github.com/pion/srtp/v3 v3.0.4/go.mod h1:1Jx3FwDoxpRaTh1oRV8A/6G1BnFL+QI82eK4ms8EEJQ=
+github.com/pion/srtp/v3 v3.0.6 h1:E2gyj1f5X10sB/qILUGIkL4C2CqK269Xq167PbGCc/4=
+github.com/pion/srtp/v3 v3.0.6/go.mod h1:BxvziG3v/armJHAaJ87euvkhHqWe9I7iiOy50K2QkhY=
 github.com/pion/stun v0.6.1 h1:8lp6YejULeHBF8NmV8e2787BogQhduZugh5PdhDyyN4=
 github.com/pion/stun v0.6.1/go.mod h1:/hO7APkX4hZKu/D0f2lHzNyvdkTGtIy3NDmLR7kSz/8=
 github.com/pion/stun/v2 v2.0.0 h1:A5+wXKLAypxQri59+tmQKVs7+l6mMM+3d+eER9ifRU0=
@@ -948,12 +884,12 @@ github.com/pion/transport/v3 v3.0.7/go.mod h1:YleKiTZ4vqNxVwh77Z0zytYi7rXHl7j6uP
 github.com/pion/turn/v2 v2.1.3/go.mod h1:huEpByKKHix2/b9kmTAM3YoX6MKP+/D//0ClgUYR2fY=
 github.com/pion/turn/v2 v2.1.6 h1:Xr2niVsiPTB0FPtt+yAWKFUkU1eotQbGgpTIld4x1Gc=
 github.com/pion/turn/v2 v2.1.6/go.mod h1:huEpByKKHix2/b9kmTAM3YoX6MKP+/D//0ClgUYR2fY=
-github.com/pion/turn/v4 v4.0.0 h1:qxplo3Rxa9Yg1xXDxxH8xaqcyGUtbHYw4QSCvmFWvhM=
-github.com/pion/turn/v4 v4.0.0/go.mod h1:MuPDkm15nYSklKpN8vWJ9W2M0PlyQZqYt1McGuxG7mA=
+github.com/pion/turn/v4 v4.0.2 h1:ZqgQ3+MjP32ug30xAbD6Mn+/K4Sxi3SdNOTFf+7mpps=
+github.com/pion/turn/v4 v4.0.2/go.mod h1:pMMKP/ieNAG/fN5cZiN4SDuyKsXtNTr0ccN7IToA1zs=
 github.com/pion/webrtc/v3 v3.3.5 h1:ZsSzaMz/i9nblPdiAkZoP+E6Kmjw+jnyq3bEmU3EtRg=
 github.com/pion/webrtc/v3 v3.3.5/go.mod h1:liNa+E1iwyzyXqNUwvoMRNQ10x8h8FOeJKL8RkIbamE=
-github.com/pion/webrtc/v4 v4.0.8 h1:T1ZmnT9qxIJIt4d8XoiMOBrTClGHDDXNg9e/fh018Qc=
-github.com/pion/webrtc/v4 v4.0.8/go.mod h1:HHBeUVBAC+j4ZFnYhovEFStF02Arb1EyD4G7e7HBTJw=
+github.com/pion/webrtc/v4 v4.1.2 h1:mpuUo/EJ1zMNKGE79fAdYNFZBX790KE7kQQpLMjjR54=
+github.com/pion/webrtc/v4 v4.1.2/go.mod h1:xsCXiNAmMEjIdFxAYU0MbB3RwRieJsegSB2JZsGN+8U=
 github.com/pkg/diff v0.0.0-20210226163009-20ebb0f2a09e/go.mod h1:pJLUxLENpZxwdsKMEsNbx1VGcRFpLqf3715MtcvvzbA=
 github.com/pkg/errors v0.8.0/go.mod h1:bwawxfHBFNV+L2hUp1rHADufV3IMtnDRdf1r5NINEl0=
 github.com/pkg/errors v0.8.1/go.mod h1:bwawxfHBFNV+L2hUp1rHADufV3IMtnDRdf1r5NINEl0=
@@ -969,51 +905,46 @@ github.com/power-devops/perfstat v0.0.0-20210106213030-5aafc221ea8c h1:ncq/mPwQF
 github.com/power-devops/perfstat v0.0.0-20210106213030-5aafc221ea8c/go.mod h1:OmDBASR4679mdNQnz2pUhc2G8CO2JrUAVFDRBDP/hJE=
 github.com/prashantv/gostub v1.1.0 h1:BTyx3RfQjRHnUWaGF9oQos79AlQ5k8WNktv7VGvVH4g=
 github.com/prashantv/gostub v1.1.0/go.mod h1:A5zLQHz7ieHGG7is6LLXLz7I8+3LZzsrV0P1IAHhP5U=
-github.com/prometheus/client_golang v0.8.0/go.mod h1:7SWBe2y4D6OKWSNQJUaRYU/AaXPKyh/dDVn+NZz0KFw=
 github.com/prometheus/client_golang v0.9.1/go.mod h1:7SWBe2y4D6OKWSNQJUaRYU/AaXPKyh/dDVn+NZz0KFw=
 github.com/prometheus/client_golang v0.9.2/go.mod h1:OsXs2jCmiKlQ1lTBmv21f2mNfw4xf/QclQDMrYNZzcM=
 github.com/prometheus/client_golang v0.9.3-0.20190127221311-3c4408c8b829/go.mod h1:p2iRAGwDERtqlqzRXnrOVns+ignqQo//hLXqYxZYVNs=
 github.com/prometheus/client_golang v1.0.0/go.mod h1:db9x61etRT2tGnBNRi70OPL5FsnadC4Ky3P0J6CfImo=
 github.com/prometheus/client_golang v1.5.1/go.mod h1:e9GMxYsXl05ICDXkRhurwBS4Q3OK1iX/F2sw+iXX5zU=
-github.com/prometheus/client_golang v1.20.5 h1:cxppBPuYhUnsO6yo/aoRol4L7q7UFfdm+bR9r+8l63Y=
-github.com/prometheus/client_golang v1.20.5/go.mod h1:PIEt8X02hGcP8JWbeHyeZ53Y/jReSnHgO035n//V5WE=
+github.com/prometheus/client_golang v1.22.0 h1:rb93p9lokFEsctTys46VnV1kLCDpVZ0a/Y92Vm0Zc6Q=
+github.com/prometheus/client_golang v1.22.0/go.mod h1:R7ljNsLXhuQXYZYtw6GAE9AZg8Y7vEW5scdCXrWRXC0=
 github.com/prometheus/client_model v0.0.0-20180712105110-5c3871d89910/go.mod h1:MbSGuTsp3dbXC40dX6PRTWyKYBIrTGTE9sqQNg2J8bo=
 github.com/prometheus/client_model v0.0.0-20190115171406-56726106282f/go.mod h1:MbSGuTsp3dbXC40dX6PRTWyKYBIrTGTE9sqQNg2J8bo=
 github.com/prometheus/client_model v0.0.0-20190129233127-fd36f4220a90/go.mod h1:xMI15A0UPsDsEKsMN9yxemIoYk6Tm2C1GtYGdfGttqA=
 github.com/prometheus/client_model v0.0.0-20190812154241-14fe0d1b01d4/go.mod h1:xMI15A0UPsDsEKsMN9yxemIoYk6Tm2C1GtYGdfGttqA=
 github.com/prometheus/client_model v0.2.0/go.mod h1:xMI15A0UPsDsEKsMN9yxemIoYk6Tm2C1GtYGdfGttqA=
-github.com/prometheus/client_model v0.6.1 h1:ZKSh/rekM+n3CeS952MLRAdFwIKqeY8b62p8ais2e9E=
-github.com/prometheus/client_model v0.6.1/go.mod h1:OrxVMOVHjw3lKMa8+x6HeMGkHMQyHDk9E3jmP2AmGiY=
-github.com/prometheus/common v0.0.0-20180801064454-c7de2306084e/go.mod h1:daVV7qP5qjZbuso7PdcryaAu0sAZbrN9i7WWcTMWvro=
+github.com/prometheus/client_model v0.6.2 h1:oBsgwpGs7iVziMvrGhE53c/GrLUsZdHnqNwqPLxwZyk=
+github.com/prometheus/client_model v0.6.2/go.mod h1:y3m2F6Gdpfy6Ut/GBsUqTWZqCUvMVzSfMLjcu6wAwpE=
 github.com/prometheus/common v0.0.0-20181126121408-4724e9255275/go.mod h1:daVV7qP5qjZbuso7PdcryaAu0sAZbrN9i7WWcTMWvro=
 github.com/prometheus/common v0.2.0/go.mod h1:TNfzLD0ON7rHzMJeJkieUDPYmFC7Snx/y86RQel1bk4=
 github.com/prometheus/common v0.4.1/go.mod h1:TNfzLD0ON7rHzMJeJkieUDPYmFC7Snx/y86RQel1bk4=
 github.com/prometheus/common v0.9.1/go.mod h1:yhUN8i9wzaXS3w1O07YhxHEBxD+W35wd8bs7vj7HSQ4=
-github.com/prometheus/common v0.62.0 h1:xasJaQlnWAeyHdUBeGjXmutelfJHWMRr+Fg4QszZ2Io=
-github.com/prometheus/common v0.62.0/go.mod h1:vyBcEuLSvWos9B1+CyL7JZ2up+uFzXhkqml0W5zIY1I=
-github.com/prometheus/procfs v0.0.0-20180725123919-05ee40e3a273/go.mod h1:c3At6R/oaqEKCNdg8wHV1ftS6bRYblBhIjjI8uT2IGk=
+github.com/prometheus/common v0.64.0 h1:pdZeA+g617P7oGv1CzdTzyeShxAGrTBsolKNOLQPGO4=
+github.com/prometheus/common v0.64.0/go.mod h1:0gZns+BLRQ3V6NdaerOhMbwwRbNh9hkGINtQAsP5GS8=
 github.com/prometheus/procfs v0.0.0-20181005140218-185b4288413d/go.mod h1:c3At6R/oaqEKCNdg8wHV1ftS6bRYblBhIjjI8uT2IGk=
 github.com/prometheus/procfs v0.0.0-20181204211112-1dc9a6cbc91a/go.mod h1:c3At6R/oaqEKCNdg8wHV1ftS6bRYblBhIjjI8uT2IGk=
 github.com/prometheus/procfs v0.0.0-20190117184657-bf6a532e95b1/go.mod h1:c3At6R/oaqEKCNdg8wHV1ftS6bRYblBhIjjI8uT2IGk=
 github.com/prometheus/procfs v0.0.2/go.mod h1:TjEm7ze935MbeOT/UhFTIMYKhuLP4wbCsTZCD3I8kEA=
 github.com/prometheus/procfs v0.0.8/go.mod h1:7Qr8sr6344vo1JqZ6HhLceV9o3AJ1Ff+GxbHq6oeK9A=
 github.com/prometheus/procfs v0.0.11/go.mod h1:lV6e/gmhEcM9IjHGsFOCxxuZ+z1YqCvr4OA4YeYWdaU=
-github.com/prometheus/procfs v0.15.1 h1:YagwOFzUgYfKKHX6Dr+sHT7km/hxC76UB0learggepc=
-github.com/prometheus/procfs v0.15.1/go.mod h1:fB45yRUv8NstnjriLhBQLuOUt+WW4BsoGhij/e3PBqk=
+github.com/prometheus/procfs v0.16.1 h1:hZ15bTNuirocR6u0JZ6BAHHmwS1p8B4P6MRqxtzMyRg=
+github.com/prometheus/procfs v0.16.1/go.mod h1:teAbpZRB1iIAJYREa1LsoWUXykVXA1KlTmWl8x/U+Is=
 github.com/protolambda/ztyp v0.2.2 h1:rVcL3vBu9W/aV646zF6caLS/dyn9BN8NYiuJzicLNyY=
 github.com/protolambda/ztyp v0.2.2/go.mod h1:9bYgKGqg3wJqT9ac1gI2hnVb0STQq7p/1lapqrqY1dU=
 github.com/prysmaticlabs/gohashtree v0.0.3-alpha.0.20230502123415-aafd8b3ca202 h1:ZsFouPKy81vvQo/Zup5gASVdOm6aiuwUhp7GxvQmjIA=
 github.com/prysmaticlabs/gohashtree v0.0.3-alpha.0.20230502123415-aafd8b3ca202/go.mod h1:4pWaT30XoEx1j8KNJf3TV+E3mQkaufn7mf+jRNb/Fuk=
 github.com/quasilyte/go-ruleguard/dsl v0.3.22 h1:wd8zkOhSNr+I+8Qeciml08ivDt1pSXe60+5DqOpCjPE=
 github.com/quasilyte/go-ruleguard/dsl v0.3.22/go.mod h1:KeCP03KrjuSO0H1kTuZQCWlQPulDV6YMIXmpQss17rU=
-github.com/quic-go/qpack v0.5.1 h1:giqksBPnT/HDtZ6VhtFKgoLOWmlyo9Ei6u9PqzIMbhI=
-github.com/quic-go/qpack v0.5.1/go.mod h1:+PC4XFrEskIVkcLzpEkbLqq1uCoxPhQuvK5rH1ZgaEg=
-github.com/quic-go/quic-go v0.49.0 h1:w5iJHXwHxs1QxyBv1EHKuC50GX5to8mJAxvtnttJp94=
-github.com/quic-go/quic-go v0.49.0/go.mod h1:s2wDnmCdooUQBmQfpUSTCYBl1/D4FcqbULMMkASvR6s=
-github.com/quic-go/webtransport-go v0.8.1-0.20241018022711-4ac2c9250e66 h1:4WFk6u3sOT6pLa1kQ50ZVdm8BQFgJNA117cepZxtLIg=
-github.com/quic-go/webtransport-go v0.8.1-0.20241018022711-4ac2c9250e66/go.mod h1:Vp72IJajgeOL6ddqrAhmp7IM9zbTcgkQxD/YdxrVwMw=
-github.com/raulk/go-watchdog v1.3.0 h1:oUmdlHxdkXRJlwfG0O9omj8ukerm8MEQavSiDTEtBsk=
-github.com/raulk/go-watchdog v1.3.0/go.mod h1:fIvOnLbF0b0ZwkB9YU4mOW9Did//4vPZtDqv66NfsMU=
+github.com/quic-go/qpack v0.6.0 h1:g7W+BMYynC1LbYLSqRt8PBg5Tgwxn214ZZR34VIOjz8=
+github.com/quic-go/qpack v0.6.0/go.mod h1:lUpLKChi8njB4ty2bFLX2x4gzDqXwUpaO1DP9qMDZII=
+github.com/quic-go/quic-go v0.57.1 h1:25KAAR9QR8KZrCZRThWMKVAwGoiHIrNbT72ULHTuI10=
+github.com/quic-go/quic-go v0.57.1/go.mod h1:ly4QBAjHA2VhdnxhojRsCUOeJwKYg+taDlos92xb1+s=
+github.com/quic-go/webtransport-go v0.9.0 h1:jgys+7/wm6JarGDrW+lD/r9BGqBAmqY/ssklE09bA70=
+github.com/quic-go/webtransport-go v0.9.0/go.mod h1:4FUYIiUc75XSsF6HShcLeXXYZJ9AGwo/xh3L8M/P1ao=
 github.com/rcrowley/go-metrics v0.0.0-20181016184325-3113b8401b8a/go.mod h1:bCqnVzQkZxMG4s8nGwiZ5l3QUCyqpo9Y+/ZMZ9VjZe4=
 github.com/remyoudompheng/bigfft v0.0.0-20230129092748-24d4a6f8daec h1:W09IVJc94icq4NjY3clb7Lk8O1qJ8BdBEF8z0ibU0rE=
 github.com/remyoudompheng/bigfft v0.0.0-20230129092748-24d4a6f8daec/go.mod h1:qqbHyh8v60DhA7CoWK5oRCqLrMHRGoxYCSS9EjAz6Eo=
@@ -1031,8 +962,6 @@ github.com/rs/cors v1.11.0 h1:0B9GE/r9Bc2UxRMMtymBkHTenPkHDv0CW4Y98GBY+po=
 github.com/rs/cors v1.11.0/go.mod h1:XyqrcTp5zjWr1wsJ8PIRZssZ8b/WMcMf71DJnit4EMU=
 github.com/rs/dnscache v0.0.0-20211102005908-e0241e321417 h1:Lt9DzQALzHoDwMBGJ6v8ObDPR0dzr2a6sXTB1Fq7IHs=
 github.com/rs/dnscache v0.0.0-20211102005908-e0241e321417/go.mod h1:qe5TWALJ8/a1Lqznoc5BDHpYX/8HU60Hm2AwRmqzxqA=
-github.com/russross/blackfriday v1.5.2 h1:HyvC0ARfnZBqnXwABFeSZHpKvJHJJfPz81GNueLj0oo=
-github.com/russross/blackfriday v1.5.2/go.mod h1:JO/DiYxRf+HjHt06OyowR9PTA263kcR/rfWxYHBV53g=
 github.com/russross/blackfriday/v2 v2.0.1/go.mod h1:+Rmxgy9KzJVeS9/2gXHxylqXiyQDYRxCVz55jmeOWTM=
 github.com/russross/blackfriday/v2 v2.1.0 h1:JIOH55/0cWyOuilr9/qlrm0BSXldqnqwMsf35Ld67mk=
 github.com/russross/blackfriday/v2 v2.1.0/go.mod h1:+Rmxgy9KzJVeS9/2gXHxylqXiyQDYRxCVz55jmeOWTM=
@@ -1043,7 +972,6 @@ github.com/ryszard/goskiplist v0.0.0-20150312221310-2dfbae5fcf46 h1:GHRpF1pTW19a
 github.com/ryszard/goskiplist v0.0.0-20150312221310-2dfbae5fcf46/go.mod h1:uAQ5PCi+MFsC7HjREoAz1BU+Mq60+05gifQSsHSDG/8=
 github.com/schollz/progressbar/v2 v2.15.0 h1:dVzHQ8fHRmtPjD3K10jT3Qgn/+H+92jhPrhmxIJfDz8=
 github.com/schollz/progressbar/v2 v2.15.0/go.mod h1:UdPq3prGkfQ7MOzZKlDRpYKcFqEMczbD7YmbPgpzKMI=
-github.com/sergi/go-diff v1.0.0/go.mod h1:0CfEIISq7TuYL3j771MWULgwwjU+GofnZX9QAmXWZgo=
 github.com/shirou/gopsutil v3.21.4-0.20210419000835-c7a38de76ee5+incompatible h1:Bn1aCHHRnjv4Bl16T8rcaFjYSrGrIZvpiGO6P3Q4GpU=
 github.com/shirou/gopsutil v3.21.4-0.20210419000835-c7a38de76ee5+incompatible/go.mod h1:5b4v6he4MtMOwMlS0TUMTu2PcXUg8+E1lC7eC3UO/RA=
 github.com/shirou/gopsutil/v3 v3.24.3 h1:eoUGJSmdfLzJ3mxIhmOAhgKEKgQkeOwKpz1NbhVnuPE=
@@ -1054,32 +982,9 @@ github.com/shoenig/go-m1cpu v0.1.6 h1:nxdKQNcEB6vzgA2E2bvzKIYRuNj7XNJ4S/aRSwKzFt
 github.com/shoenig/go-m1cpu v0.1.6/go.mod h1:1JJMcUBvfNwpq05QDQVAnx3gUHr9IYF7GNg9SUEw2VQ=
 github.com/shoenig/test v0.6.4 h1:kVTaSd7WLz5WZ2IaoM0RSzRsUD+m8wRR+5qvntpn4LU=
 github.com/shoenig/test v0.6.4/go.mod h1:byHiCGXqrVaflBLAMq/srcZIHynQPQgeyvkvXnjqq0k=
-github.com/shurcooL/component v0.0.0-20170202220835-f88ec8f54cc4/go.mod h1:XhFIlyj5a1fBNx5aJTbKoIq0mNaPvOagO+HjB3EtxrY=
-github.com/shurcooL/events v0.0.0-20181021180414-410e4ca65f48/go.mod h1:5u70Mqkb5O5cxEA8nxTsgrgLehJeAw6Oc4Ab1c/P1HM=
-github.com/shurcooL/github_flavored_markdown v0.0.0-20181002035957-2122de532470/go.mod h1:2dOwnU2uBioM+SGy2aZoq1f/Sd1l9OkAeAUvjSyvgU0=
-github.com/shurcooL/go v0.0.0-20180423040247-9e1955d9fb6e/go.mod h1:TDJrrUr11Vxrven61rcy3hJMUqaf/CLWYhHNPmT14Lk=
-github.com/shurcooL/go-goon v0.0.0-20170922171312-37c2f522c041/go.mod h1:N5mDOmsrJOB+vfqUK+7DmDyjhSLIIBnXo9lvZJj3MWQ=
-github.com/shurcooL/gofontwoff v0.0.0-20180329035133-29b52fc0a18d/go.mod h1:05UtEgK5zq39gLST6uB0cf3NEHjETfB4Fgr3Gx5R9Vw=
-github.com/shurcooL/gopherjslib v0.0.0-20160914041154-feb6d3990c2c/go.mod h1:8d3azKNyqcHP1GaQE/c6dDgjkgSx2BZ4IoEi4F1reUI=
-github.com/shurcooL/highlight_diff v0.0.0-20170515013008-09bb4053de1b/go.mod h1:ZpfEhSmds4ytuByIcDnOLkTHGUI6KNqRNPDLHDk+mUU=
-github.com/shurcooL/highlight_go v0.0.0-20181028180052-98c3abbbae20/go.mod h1:UDKB5a1T23gOMUJrI+uSuH0VRDStOiUVSjBTRDVBVag=
-github.com/shurcooL/home v0.0.0-20181020052607-80b7ffcb30f9/go.mod h1:+rgNQw2P9ARFAs37qieuu7ohDNQ3gds9msbT2yn85sg=
-github.com/shurcooL/htmlg v0.0.0-20170918183704-d01228ac9e50/go.mod h1:zPn1wHpTIePGnXSHpsVPWEktKXHr6+SS6x/IKRb7cpw=
-github.com/shurcooL/httperror v0.0.0-20170206035902-86b7830d14cc/go.mod h1:aYMfkZ6DWSJPJ6c4Wwz3QtW22G7mf/PEgaB9k/ik5+Y=
-github.com/shurcooL/httpfs v0.0.0-20171119174359-809beceb2371/go.mod h1:ZY1cvUeJuFPAdZ/B6v7RHavJWZn2YPVFQ1OSXhCGOkg=
-github.com/shurcooL/httpgzip v0.0.0-20180522190206-b1c53ac65af9/go.mod h1:919LwcH0M7/W4fcZ0/jy0qGght1GIhqyS/EgWGH2j5Q=
-github.com/shurcooL/issues v0.0.0-20181008053335-6292fdc1e191/go.mod h1:e2qWDig5bLteJ4fwvDAc2NHzqFEthkqn7aOZAOpj+PQ=
-github.com/shurcooL/issuesapp v0.0.0-20180602232740-048589ce2241/go.mod h1:NPpHK2TI7iSaM0buivtFUc9offApnI0Alt/K8hcHy0I=
-github.com/shurcooL/notifications v0.0.0-20181007000457-627ab5aea122/go.mod h1:b5uSkrEVM1jQUspwbixRBhaIjIzL2xazXp6kntxYle0=
-github.com/shurcooL/octicon v0.0.0-20181028054416-fa4f57f9efb2/go.mod h1:eWdoE5JD4R5UVWDucdOPg1g2fqQRq78IQa9zlOV1vpQ=
-github.com/shurcooL/reactions v0.0.0-20181006231557-f2e0b4ca5b82/go.mod h1:TCR1lToEk4d2s07G3XGfz2QrgHXg4RJBvjrOozvoWfk=
-github.com/shurcooL/sanitized_anchor_name v0.0.0-20170918181015-86672fcb3f95/go.mod h1:1NzhyTcUVG4SuEtjjoZeVRXNmyL/1OwPU0+IJeTBvfc=
 github.com/shurcooL/sanitized_anchor_name v1.0.0/go.mod h1:1NzhyTcUVG4SuEtjjoZeVRXNmyL/1OwPU0+IJeTBvfc=
-github.com/shurcooL/users v0.0.0-20180125191416-49c67e49c537/go.mod h1:QJTqeLYEDaXHZDBsXlPCDqdhQuJkuw4NOtaxYe3xii4=
-github.com/shurcooL/webdavfs v0.0.0-20170829043945-18c3829fa133/go.mod h1:hKmq5kWdCj2z2KEozexVbfEZIWiTjhE0+UjmZgPqehw=
 github.com/sirupsen/logrus v1.2.0/go.mod h1:LxeOpSwHxABJmUn/MG1IvRgCAasNZTLOkJPxbbu5VWo=
 github.com/sirupsen/logrus v1.4.2/go.mod h1:tLMulIdttU9McNUspp0xgXVQah82FyeX6MwdIuYE2rE=
-github.com/sirupsen/logrus v1.7.0/go.mod h1:yWOB1SBYBC5VeMP7gHvWumXLIWorT60ONWic61uBYv0=
 github.com/sirupsen/logrus v1.9.3 h1:dueUQJ1C2q9oE3F7wvmSGAaVtTmUizReu6fjN8uqzbQ=
 github.com/sirupsen/logrus v1.9.3/go.mod h1:naHLuLoDiP4jHNo9R0sCBMtWGeIprob74mVsIT4qYEQ=
 github.com/smartystreets/assertions v0.0.0-20180927180507-b2de0cb4f26d/go.mod h1:OnSkiWE9lh6wB0YB77sQom3nweQdgAjqCqsofrRNTgc=
@@ -1091,16 +996,15 @@ github.com/smartystreets/goconvey v0.0.0-20190306220146-200a235640ff/go.mod h1:K
 github.com/smartystreets/goconvey v1.6.4/go.mod h1:syvi0/a8iFYH4r/RixwvyeAJjdLS9QV7WQ/tjFTllLA=
 github.com/smartystreets/goconvey v1.7.2 h1:9RBaZCeXEQ3UselpuwUQHltGVXvdwm6cv1hgR6gDIPg=
 github.com/smartystreets/goconvey v1.7.2/go.mod h1:Vw0tHAZW6lzCRk3xgdin6fKYcG+G3Pg9vgXWeJpQFMM=
-github.com/sourcegraph/annotate v0.0.0-20160123013949-f4cad6c6324d/go.mod h1:UdhH50NIW0fCiwBSr0co2m7BnFLdv4fQTgdqdJTHFeE=
-github.com/sourcegraph/syntaxhighlight v0.0.0-20170531221838-bd320f5d308e/go.mod h1:HuIsMU8RRBOtsCgI77wP899iHVBQpCmg4ErYMZB+2IA=
 github.com/spaolacci/murmur3 v1.1.0 h1:7c1g84S4BPRrfL5Xrdp6fOJ206sU9y293DDHaoy0bLI=
 github.com/spaolacci/murmur3 v1.1.0/go.mod h1:JwIasOWyU6f++ZhiEuf87xNszmSA2myDM2Kzu9HwQUA=
 github.com/spf13/afero v1.9.5 h1:stMpOSZFs//0Lv29HduCmli3GUfpFoF3Y1Q/aXj/wVM=
 github.com/spf13/afero v1.9.5/go.mod h1:UBogFpq8E9Hx+xc5CNTTEpTnuHVmXDwZcZcE1eb/UhQ=
 github.com/spf13/cobra v1.8.1 h1:e5/vxKd/rZsfSJMUX1agtjeTDf+qv1/JdBF8gg5k9ZM=
 github.com/spf13/cobra v1.8.1/go.mod h1:wHxEcudfqmLYa8iTfL+OuZPbBZkmvliBWKIezN3kD9Y=
-github.com/spf13/pflag v1.0.5 h1:iy+VFUOCP1a+8yFto/drg2CJ5u0yRoB7fZw3DKv/JXA=
 github.com/spf13/pflag v1.0.5/go.mod h1:McXfInJRrz4CZXVZOBLb0bTZqETkiAhM9Iw0y3An2Bg=
+github.com/spf13/pflag v1.0.6 h1:jFzHGLGAlb3ruxLB8MhbI6A8+AQX/2eW4qeyNZXNp2o=
+github.com/spf13/pflag v1.0.6/go.mod h1:McXfInJRrz4CZXVZOBLb0bTZqETkiAhM9Iw0y3An2Bg=
 github.com/stretchr/objx v0.1.0/go.mod h1:HFkY916IF+rwdDfMAkV7OtwuqBVzrE8GR6GFx+wExME=
 github.com/stretchr/objx v0.1.1/go.mod h1:HFkY916IF+rwdDfMAkV7OtwuqBVzrE8GR6GFx+wExME=
 github.com/stretchr/objx v0.4.0/go.mod h1:YvHI0jy2hoMjB+UWwv71VJQ9isScKT/TqJzVSSt89Yw=
@@ -1121,13 +1025,12 @@ github.com/stretchr/testify v1.8.1/go.mod h1:w2LPCIKwWwSfY2zedu0+kehJoqGctiVI29o
 github.com/stretchr/testify v1.8.3/go.mod h1:sz/lmYIOXD/1dqDmKjjqLyZ2RngseejIcXlSw2iwfAo=
 github.com/stretchr/testify v1.8.4/go.mod h1:sz/lmYIOXD/1dqDmKjjqLyZ2RngseejIcXlSw2iwfAo=
 github.com/stretchr/testify v1.9.0/go.mod h1:r2ic/lqez/lEtzL7wO/rwa5dbSLXVDPFyf8C91i36aY=
-github.com/stretchr/testify v1.10.0 h1:Xv5erBjTwe/5IxqUQTdXv5kgmIvbHo3QQyRwhJsOfJA=
-github.com/stretchr/testify v1.10.0/go.mod h1:r2ic/lqez/lEtzL7wO/rwa5dbSLXVDPFyf8C91i36aY=
+github.com/stretchr/testify v1.11.1 h1:7s2iGBzp5EwR7/aIZr8ao5+dra3wiQyKjjFuvgVKu7U=
+github.com/stretchr/testify v1.11.1/go.mod h1:wZwfW3scLgRK+23gO65QZefKpKQRnfz6sD981Nm4B6U=
 github.com/supranational/blst v0.3.15 h1:rd9viN6tfARE5wv3KZJ9H8e1cg0jXW8syFCcsbHa76o=
 github.com/supranational/blst v0.3.15/go.mod h1:jZJtfjgudtNl4en1tzwPIV3KjUnQUvG3/j+w+fVonLw=
 github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7 h1:epCh84lMvA70Z7CTTCmYQn2CKbY8j86K7/FAIr141uY=
 github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7/go.mod h1:q4W45IWZaF22tdD+VEXcAWRA037jwmWEB5VWYORlTpc=
-github.com/tarm/serial v0.0.0-20180830185346-98f6abe2eb07/go.mod h1:kDXzergiv9cbyO7IOYJZWg1U88JhDg3PB6klq9Hg2pA=
 github.com/thomaso-mirodin/intmath v0.0.0-20160323211736-5dc6d854e46e h1:cR8/SYRgyQCt5cNCMniB/ZScMkhI9nk8U5C7SbISXjo=
 github.com/thomaso-mirodin/intmath v0.0.0-20160323211736-5dc6d854e46e/go.mod h1:Tu4lItkATkonrYuvtVjG0/rhy15qrNGNTjPdaphtZ/8=
 github.com/tidwall/btree v1.6.0 h1:LDZfKfQIBHGHWSwckhXI0RPSXzlo+KYdjK7FWSqOzzg=
@@ -1161,15 +1064,12 @@ github.com/uptrace/opentelemetry-go-extra/otelutil v0.2.2 h1:CNznWHkrbA6o1q2H/Bs
 github.com/uptrace/opentelemetry-go-extra/otelutil v0.2.2/go.mod h1:7YSrHCmYPHIXjTWnKSU7EGT0TFEcm3WwSeQquwCGg38=
 github.com/uptrace/opentelemetry-go-extra/otelzap v0.2.2 h1:uyrW06oJi4iWvhjPLVfk4qrSP2Zm0AMozKKDmp6i4pE=
 github.com/uptrace/opentelemetry-go-extra/otelzap v0.2.2/go.mod h1:PMAs2dNxP55lgt6xu0if+Jasm6s+Xpmqn6ev1NyDfnI=
-github.com/urfave/cli v1.22.2/go.mod h1:Gos4lmkARVdJ6EkW0WaNv/tZAAMe9V7XWyB60NtXRu0=
 github.com/urfave/cli v1.22.10 h1:p8Fspmz3iTctJstry1PYS3HVdllxnEzTEsgIgtxTrCk=
 github.com/urfave/cli v1.22.10/go.mod h1:Gos4lmkARVdJ6EkW0WaNv/tZAAMe9V7XWyB60NtXRu0=
 github.com/urfave/cli/v2 v2.27.5 h1:WoHEJLdsXr6dDWoJgMq/CboDmyY/8HMMH1fTECbih+w=
 github.com/urfave/cli/v2 v2.27.5/go.mod h1:3Sevf16NykTbInEnD0yKkjDAeZDS0A6bzhBH5hrMvTQ=
 github.com/valyala/fastjson v1.6.4 h1:uAUNq9Z6ymTgGhcm0UynUAB6tlbakBrz6CQFax3BXVQ=
 github.com/valyala/fastjson v1.6.4/go.mod h1:CLCAqky6SMuOcxStkYQvblddUtoRxhYMGLrsQns1aXY=
-github.com/viant/assertly v0.4.8/go.mod h1:aGifi++jvCrUaklKEKT0BU95igDNaqkvz+49uaYMPRU=
-github.com/viant/toolbox v0.24.0/go.mod h1:OxMCG57V0PXuIP2HNQrtJf2CjqdmbrOx5EkMILuUhzM=
 github.com/warpfork/go-wish v0.0.0-20220906213052-39a1cc7a02d0 h1:GDDkbFiaK8jsSDJfjId/PEGEShv6ugrt4kYsC5UIDaQ=
 github.com/warpfork/go-wish v0.0.0-20220906213052-39a1cc7a02d0/go.mod h1:x6AKhvSSexNrVSrViXSHUEbICjmGXhtgABaHIySUSGw=
 github.com/whyrusleeping/go-keyspace v0.0.0-20160322163242-5b898ac5add1 h1:EKhdznlJHPMoKr0XTrX+IlJs1LH3lyx2nfr1dOlZ79k=
@@ -1195,7 +1095,6 @@ go.elastic.co/ecszap v1.0.0 h1:PdQkRUeraR3XHJ14T7JMa+ncU0XXrVrcEN/BoRa2nMI=
 go.elastic.co/ecszap v1.0.0/go.mod h1:HTUi+QRmr3EuZMqxPX+5fyOdMNfUu5iPebgfhgsTJYQ=
 go.etcd.io/bbolt v1.3.6 h1:/ecaJf0sk1l4l6V4awd65v2C3ILy7MSj+s/x1ADCIMU=
 go.etcd.io/bbolt v1.3.6/go.mod h1:qXsaaIqmgQH0T+OPdb99Bf+PKfBBQVAdyD6TY9G8XM4=
-go.opencensus.io v0.18.0/go.mod h1:vKdFvxhtzZ9onBp9VKHK8z/sRpBMnKAsufL7wlDrCOA=
 go.opencensus.io v0.20.1/go.mod h1:6WKK9ahsWS3RSO+PY9ZHZUfv2irvY6gN279GOPZjmmk=
 go.opencensus.io v0.20.2/go.mod h1:6WKK9ahsWS3RSO+PY9ZHZUfv2irvY6gN279GOPZjmmk=
 go.opencensus.io v0.21.0/go.mod h1:mSImk1erAIZhrmZN+AvHh14ztQfjbGwt4TtuofqLduU=
@@ -1232,10 +1131,10 @@ go.uber.org/automaxprocs v1.5.2 h1:2LxUOGiR3O6tw8ui5sZa2LAaHnsviZdVOUZw4fvbnME=
 go.uber.org/automaxprocs v1.5.2/go.mod h1:eRbA25aqJrxAbsLO0xy5jVwPt7FQnRgjW+efnwa1WM0=
 go.uber.org/config v1.3.1 h1:XlXqnaD0HTGVq5Ad+sfxA/18XVG1v4mfEelYOkbKwcY=
 go.uber.org/config v1.3.1/go.mod h1:6gdxX5xKDFII45TlqT2TubO4PvJggfUOxdnmsbrimwg=
-go.uber.org/dig v1.18.0 h1:imUL1UiY0Mg4bqbFfsRQO5G4CGRBec/ZujWTvSVp3pw=
-go.uber.org/dig v1.18.0/go.mod h1:Us0rSJiThwCv2GteUN0Q7OKvU7n5J4dxZ9JKUXozFdE=
-go.uber.org/fx v1.23.0 h1:lIr/gYWQGfTwGcSXWXu4vP5Ws6iqnNEIY+F/aFzCKTg=
-go.uber.org/fx v1.23.0/go.mod h1:o/D9n+2mLP6v1EG+qsdT1O8wKopYAsqZasju97SDFCU=
+go.uber.org/dig v1.19.0 h1:BACLhebsYdpQ7IROQ1AGPjrXcP5dF80U3gKoFzbaq/4=
+go.uber.org/dig v1.19.0/go.mod h1:Us0rSJiThwCv2GteUN0Q7OKvU7n5J4dxZ9JKUXozFdE=
+go.uber.org/fx v1.24.0 h1:wE8mruvpg2kiiL1Vqd0CC+tr0/24XIB10Iwp2lLWzkg=
+go.uber.org/fx v1.24.0/go.mod h1:AmDeGyS+ZARGKM4tlH4FY2Jr63VjbEDJHtqXTGP5hbo=
 go.uber.org/goleak v1.1.10/go.mod h1:8a7PlsEVH3e/a/GLqe5IIrQx6GzcnRmZEufDUTk4A7A=
 go.uber.org/goleak v1.1.11-0.20210813005559-691160354723/go.mod h1:cwTWslyiVhfpKIDGSZEM2HlOvcqm+tG4zioyIeLoqMQ=
 go.uber.org/goleak v1.3.0 h1:2K3zAYmnTNqV73imy9J1T3WC+gmCePx2hEGkimedGto=
@@ -1252,13 +1151,9 @@ go.uber.org/zap v1.18.1/go.mod h1:xg/QME4nWcxGxrpdeYfq7UvYrLh66cuVKdrbD1XF/NI=
 go.uber.org/zap v1.19.1/go.mod h1:j3DNczoxDZroyBnOT1L/Q79cfUMGZxlv/9dzN7SM1rI=
 go.uber.org/zap v1.27.0 h1:aJMhYGrd5QSmlpLMr2MftRKl7t8J8PTZPA732ud/XR8=
 go.uber.org/zap v1.27.0/go.mod h1:GB2qFLM7cTU87MWRP2mPIjqfIDnGu+VIO4V/SdhGo2E=
-go4.org v0.0.0-20180809161055-417644f6feb5/go.mod h1:MkTOUMDaeVYJUOUsaDXIhWPZYa1yOyC1qaOBpL57BhE=
-golang.org/x/build v0.0.0-20190111050920-041ab4dc3f9d/go.mod h1:OWs+y06UdEOHN4y+MfF/py+xQ/tYqIWW03b70/CG9Rw=
 golang.org/x/crypto v0.0.0-20170930174604-9419663f5a44/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
 golang.org/x/crypto v0.0.0-20180904163835-0709b304e793/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
-golang.org/x/crypto v0.0.0-20181030102418-4d3f4d9ffa16/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
 golang.org/x/crypto v0.0.0-20190308221718-c2843e01d9a2/go.mod h1:djNgcEr1/C05ACkg1iLfiJU5Ep61QUkGW8qpdssI0+w=
-golang.org/x/crypto v0.0.0-20190313024323-a1f597ede03a/go.mod h1:djNgcEr1/C05ACkg1iLfiJU5Ep61QUkGW8qpdssI0+w=
 golang.org/x/crypto v0.0.0-20190418165655-df01cb2cc480/go.mod h1:WFFai1msRO1wXaEeE5yQxYXgSfI8pQAWXbQop6sCtWE=
 golang.org/x/crypto v0.0.0-20190510104115-cbcb75029529/go.mod h1:yigFU9vqHzYiE8UmvKecakEJjdnWj3jj499lnFckfCI=
 golang.org/x/crypto v0.0.0-20190605123033-f99c8df09eb5/go.mod h1:yigFU9vqHzYiE8UmvKecakEJjdnWj3jj499lnFckfCI=
@@ -1275,8 +1170,8 @@ golang.org/x/crypto v0.0.0-20220722155217-630584e8d5aa/go.mod h1:IxCIyHEi3zRg3s0
 golang.org/x/crypto v0.8.0/go.mod h1:mRqEX+O9/h5TFCrQhkgjo2yKi0yYA+9ecGkdQoHrywE=
 golang.org/x/crypto v0.12.0/go.mod h1:NF0Gs7EO5K4qLn+Ylc+fih8BSTeIjAP05siRnAh98yw=
 golang.org/x/crypto v0.18.0/go.mod h1:R0j02AL6hcrfOiy9T4ZYp/rcWeMxM3L6QYxlOuEG1mg=
-golang.org/x/crypto v0.36.0 h1:AnAEvhDddvBdpY+uR+MyHmuZzzNqXSe/GvuDeob5L34=
-golang.org/x/crypto v0.36.0/go.mod h1:Y4J0ReaxCR1IMaabaSMugxJES1EpwhBHhv2bDHklZvc=
+golang.org/x/crypto v0.44.0 h1:A97SsFvM3AIwEEmTBiaxPPTYpDC47w720rdiiUvgoAU=
+golang.org/x/crypto v0.44.0/go.mod h1:013i+Nw79BMiQiMsOPcVCB5ZIJbYkerPrGnOa00tvmc=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190306152737-a1d7652674e8/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190510132918-efd6b22b2522/go.mod h1:ZjyILWgesfNpC6sMxTJOJm9Kp84zZh5NQWvqDGG3Qr8=
@@ -1287,11 +1182,10 @@ golang.org/x/exp v0.0.0-20191227195350-da58074b4299/go.mod h1:2RIsYlXP63K8oxa1u0
 golang.org/x/exp v0.0.0-20200119233911-0405dc783f0a/go.mod h1:2RIsYlXP63K8oxa1u096TMicItID8zy7Y6sNkU49FU4=
 golang.org/x/exp v0.0.0-20200207192155-f17229e696bd/go.mod h1:J/WKrq2StrnmMY6+EHIKF9dgMWnmCNThgcyBT1FY9mM=
 golang.org/x/exp v0.0.0-20200224162631-6cc2880d07d6/go.mod h1:3jZMyOhIsHpP37uCMkUooju7aAi5cS1Q23tOzKc+0MU=
-golang.org/x/exp v0.0.0-20250305212735-054e65f0b394 h1:nDVHiLt8aIbd/VzvPWN6kSOPE7+F/fNFDSXLVYkE/Iw=
-golang.org/x/exp v0.0.0-20250305212735-054e65f0b394/go.mod h1:sIifuuw/Yco/y6yb6+bDNfyeQ/MdPUy/hKEMYQV17cM=
+golang.org/x/exp v0.0.0-20250606033433-dcc06ee1d476 h1:bsqhLWFR6G6xiQcb+JoGqdKdRU6WzPWmK8E0jxTjzo4=
+golang.org/x/exp v0.0.0-20250606033433-dcc06ee1d476/go.mod h1:3//PLf8L/X+8b4vuAfHzxeRUl04Adcb341+IGKfnqS8=
 golang.org/x/image v0.0.0-20190227222117-0694c2d4d067/go.mod h1:kZ7UVZpmo3dzQBMxlp+ypCbDeSB+sBbTgSJuh5dn5js=
 golang.org/x/image v0.0.0-20190802002840-cff245a6509b/go.mod h1:FeLwcggjj3mMvU+oOTbSwawSJRM1uh48EjtB4UJZlP0=
-golang.org/x/lint v0.0.0-20180702182130-06c8688daad7/go.mod h1:UVdnD1Gm6xHRNCYTkRU2/jEulfH38KcIWyp/GAMgvoE=
 golang.org/x/lint v0.0.0-20181026193005-c67002cb31c3/go.mod h1:UVdnD1Gm6xHRNCYTkRU2/jEulfH38KcIWyp/GAMgvoE=
 golang.org/x/lint v0.0.0-20190227174305-5b3e6a55c961/go.mod h1:wehouNa3lNwaWXcvxsM5YxQ5yQlVC4a0KAMCusXpPoU=
 golang.org/x/lint v0.0.0-20190301231843-5614ed5bae6f/go.mod h1:UVdnD1Gm6xHRNCYTkRU2/jEulfH38KcIWyp/GAMgvoE=
@@ -1316,21 +1210,18 @@ golang.org/x/mod v0.4.1/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.2/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.6.0-dev.0.20220419223038-86c51ed26bb4/go.mod h1:jJ57K6gSWd91VN4djpZkiMVwK6gcyfeH4XE8wZrZaV4=
 golang.org/x/mod v0.8.0/go.mod h1:iBbtSCu2XBx23ZKBPSOrRkjjQPZFPuis4dIYUhu/chs=
-golang.org/x/mod v0.24.0 h1:ZfthKaKaT4NrhGVZHO1/WDTwGES4De8KtWO0SIbNJMU=
-golang.org/x/mod v0.24.0/go.mod h1:IXM97Txy2VM4PJ3gI61r1YEk/gAj6zAHN3AdZt6S9Ww=
+golang.org/x/mod v0.29.0 h1:HV8lRxZC4l2cr3Zq1LvtOsi/ThTgWnUk/y64QSs8GwA=
+golang.org/x/mod v0.29.0/go.mod h1:NyhrlYXJ2H4eJiRy/WDBO6HMqZQ6q9nk4JzS3NuCK+w=
 golang.org/x/net v0.0.0-20180719180050-a680a1efc54d/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180724234803-3673e40ba225/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180826012351-8a410e7b638d/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180906233101-161cd47e91fd/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
-golang.org/x/net v0.0.0-20181029044818-c44066c5c816/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
-golang.org/x/net v0.0.0-20181106065722-10aee1819953/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20181114220301-adae6a3d119a/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20181201002055-351d144fa1fc/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20190108225652-1e06a53dbb7e/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20190125091013-d26f9f9a57f3/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20190213061140-3a22650c66bd/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20190311183353-d8887717615a/go.mod h1:t9HGtf8HONx5eT2rtn7q6eTqICYqUVnKs3thJo3Qplg=
-golang.org/x/net v0.0.0-20190313220215-9f648a60d977/go.mod h1:t9HGtf8HONx5eT2rtn7q6eTqICYqUVnKs3thJo3Qplg=
 golang.org/x/net v0.0.0-20190404232315-eb5bcb51f2a3/go.mod h1:t9HGtf8HONx5eT2rtn7q6eTqICYqUVnKs3thJo3Qplg=
 golang.org/x/net v0.0.0-20190501004415-9ce7a6920f09/go.mod h1:t9HGtf8HONx5eT2rtn7q6eTqICYqUVnKs3thJo3Qplg=
 golang.org/x/net v0.0.0-20190503192946-f4e77d36d62c/go.mod h1:t9HGtf8HONx5eT2rtn7q6eTqICYqUVnKs3thJo3Qplg=
@@ -1367,16 +1258,13 @@ golang.org/x/net v0.0.0-20210405180319-a5a99cb37ef4/go.mod h1:p54w0d4576C0XHj96b
 golang.org/x/net v0.0.0-20211112202133-69e39bad7dc2/go.mod h1:9nx3DQGgdP8bBQD5qxJ1jj9UTztislL4KSBs9R2vV5Y=
 golang.org/x/net v0.0.0-20220722155237-a158d28d115b/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
 golang.org/x/net v0.6.0/go.mod h1:2Tu9+aMcznHK/AK1HMvgo6xiTLG5rD5rZLDS+rp2Bjs=
-golang.org/x/net v0.7.0/go.mod h1:2Tu9+aMcznHK/AK1HMvgo6xiTLG5rD5rZLDS+rp2Bjs=
 golang.org/x/net v0.9.0/go.mod h1:d48xBJpPfHeWQsugry2m+kC02ZBRGRgulfHnEXEuWns=
 golang.org/x/net v0.10.0/go.mod h1:0qNGK6F8kojg2nk9dLZ2mShWaEBan6FAoqfSigmmuDg=
 golang.org/x/net v0.14.0/go.mod h1:PpSgVXXLK0OxS0F31C1/tv6XNguvCrnXIDrFMspZIUI=
 golang.org/x/net v0.20.0/go.mod h1:z8BVo6PvndSri0LbOE3hAn0apkU+1YvI6E70E9jsnvY=
-golang.org/x/net v0.37.0 h1:1zLorHbz+LYj7MQlSf1+2tPIIgibq2eL5xkrGk6f+2c=
-golang.org/x/net v0.37.0/go.mod h1:ivrbrMbzFq5J41QOQh0siUuly180yBYtLp+CKbEaFx8=
+golang.org/x/net v0.47.0 h1:Mx+4dIFzqraBXUugkia1OOvlD6LemFo1ALMHjrXDOhY=
+golang.org/x/net v0.47.0/go.mod h1:/jNxtkgq5yWUGYkaZGqo27cfGZ1c5Nen03aYrrKpVRU=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
-golang.org/x/oauth2 v0.0.0-20181017192945-9dcd33a902f4/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
-golang.org/x/oauth2 v0.0.0-20181203162652-d668ce993890/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
 golang.org/x/oauth2 v0.0.0-20190226205417-e64efc72b421/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
 golang.org/x/oauth2 v0.0.0-20190604053449-0f29369cfe45/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
 golang.org/x/oauth2 v0.0.0-20191202225959-858c2ad4c8b6/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
@@ -1385,7 +1273,6 @@ golang.org/x/oauth2 v0.0.0-20200902213428-5d25da1a8d43/go.mod h1:KelEdhl1UZF7XfJ
 golang.org/x/oauth2 v0.0.0-20201109201403-9fd604954f58/go.mod h1:KelEdhl1UZF7XfJ4dDtk6s++YSgaE7mD/BuKKDLBl4A=
 golang.org/x/oauth2 v0.0.0-20201208152858-08078c50e5b5/go.mod h1:KelEdhl1UZF7XfJ4dDtk6s++YSgaE7mD/BuKKDLBl4A=
 golang.org/x/oauth2 v0.0.0-20210218202405-ba52d332ba99/go.mod h1:KelEdhl1UZF7XfJ4dDtk6s++YSgaE7mD/BuKKDLBl4A=
-golang.org/x/perf v0.0.0-20180704124530-6e6d33e29852/go.mod h1:JLpeXjPJfIyPr5TlbXLkXWLhP8nz10XfvxElABhCtcw=
 golang.org/x/sync v0.0.0-20180314180146-1d60e4601c6f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20181108010431-42b317875d0f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20181221193216-37e7f081c4d4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
@@ -1399,21 +1286,18 @@ golang.org/x/sync v0.0.0-20201207232520-09787c993a3a/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20220722155255-886fb9371eb4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.1.0/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
-golang.org/x/sync v0.12.0 h1:MHc5BpPuC30uJk597Ri8TV3CNZcTLu6B6z4lJy+g6Jw=
-golang.org/x/sync v0.12.0/go.mod h1:1dzgHSNfp02xaA81J2MS99Qcpr2w7fw1gpm99rleRqA=
-golang.org/x/sys v0.0.0-20180810173357-98c5dad5d1a0/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
+golang.org/x/sync v0.18.0 h1:kr88TuHDroi+UVf+0hZnirlk8o8T+4MrK6mr60WkH/I=
+golang.org/x/sync v0.18.0/go.mod h1:9KTHXmSnoGruLpwFjVSX0lNNA75CykiMECbovNTZqGI=
 golang.org/x/sys v0.0.0-20180823144017-11551d06cbcc/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180830151530-49385e6e1522/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180905080454-ebe1bf3edb33/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180909124046-d0be0721c37e/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
-golang.org/x/sys v0.0.0-20181029174526-d69651ed3497/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20181116152217-5ac8a444bdc5/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20181122145206-62eef0e2fa9b/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20190129075346-302c3dd5f1cc/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20190215142949-d0b11bdaac8a/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20190222072716-a9d3bda3a223/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20190312061237-fead79001313/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
-golang.org/x/sys v0.0.0-20190316082340-a2f829d7f35f/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20190403152447-81d4e9dc473e/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20190412213103-97732733099d/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20190422165155-953cdadca894/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
@@ -1427,14 +1311,12 @@ golang.org/x/sys v0.0.0-20190916202348-b4ddaad3f8a3/go.mod h1:h1NjWce9XRLGQEsW7w
 golang.org/x/sys v0.0.0-20191001151750-bb3f8db39f24/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20191005200804-aed5e4c7ecf9/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20191008105621-543471e840be/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
-golang.org/x/sys v0.0.0-20191026070338-33540a1f6037/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20191120155948-bd437916bb0e/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20191204072324-ce4227a45e2e/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20191228213918-04cbcbbfeed8/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20200106162015-b016eb3dc98e/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20200113162924-86b910548bc1/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20200122134326-e047566fdf82/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
-golang.org/x/sys v0.0.0-20200124204421-9fbb57f87de9/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20200202164722-d101bd2416d5/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20200212091648-12a6c2dcc1e4/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20200223170610-d5e6a3e2c0ae/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
@@ -1482,17 +1364,19 @@ golang.org/x/sys v0.11.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.14.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
 golang.org/x/sys v0.16.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
 golang.org/x/sys v0.18.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
-golang.org/x/sys v0.31.0 h1:ioabZlmFYtWhL+TRYpcnNlLwhyxaM9kWTDEmfnprqik=
-golang.org/x/sys v0.31.0/go.mod h1:BJP2sWEmIv4KK5OTEluFJCKSidICx8ciO85XgH3Ak8k=
+golang.org/x/sys v0.38.0 h1:3yZWxaJjBmCWXqhN1qh02AkOnCQ1poK6oF+a7xWL6Gc=
+golang.org/x/sys v0.38.0/go.mod h1:OgkHotnGiDImocRcuBABYBEXf8A9a87e/uXjp9XT3ks=
+golang.org/x/telemetry v0.0.0-20251008203120-078029d740a8 h1:LvzTn0GQhWuvKH/kVRS3R3bVAsdQWI7hvfLHGgh9+lU=
+golang.org/x/telemetry v0.0.0-20251008203120-078029d740a8/go.mod h1:Pi4ztBfryZoJEkyFTI5/Ocsu2jXyDr6iSdgJiYE/uwE=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/term v0.5.0/go.mod h1:jMB1sMXY+tzblOD4FWmEbocvup2/aLOaQEp7JmGp78k=
 golang.org/x/term v0.7.0/go.mod h1:P32HKFT3hSsZrRxla30E9HqToFYAQPCMs/zFMBUFqPY=
 golang.org/x/term v0.8.0/go.mod h1:xPskH00ivmX89bAKVGSKKtLOWNx2+17Eiy94tnKShWo=
 golang.org/x/term v0.11.0/go.mod h1:zC9APTIj3jG3FdV/Ons+XE1riIZXG4aZ4GTHiPZJPIU=
 golang.org/x/term v0.16.0/go.mod h1:yn7UURbUtPyrVJPGPq404EukNFxcm/foM+bV/bfcDsY=
-golang.org/x/term v0.30.0 h1:PQ39fJZ+mfadBm0y5WlL4vlM7Sx1Hgf13sMIY2+QS9Y=
-golang.org/x/term v0.30.0/go.mod h1:NYYFdzHoI5wRh/h5tDMdMqCqPJZEuNqVR5xJLd/n67g=
+golang.org/x/term v0.37.0 h1:8EGAD0qCmHYZg6J17DvsMy9/wJ7/D/4pV/wfnld5lTU=
+golang.org/x/term v0.37.0/go.mod h1:5pB4lxRNYYVZuTLmy8oR2BH8dflOR+IbTYFD8fi3254=
 golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.1-0.20180807135948-17ff2d5776d2/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
@@ -1506,19 +1390,16 @@ golang.org/x/text v0.7.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
 golang.org/x/text v0.9.0/go.mod h1:e1OnstbJyHTd6l/uOt8jFFHp6TRDWZR/bV3emEE/zU8=
 golang.org/x/text v0.12.0/go.mod h1:TvPlkZtksWOMsz7fbANvkp4WM8x/WCo/om8BMLbz+aE=
 golang.org/x/text v0.14.0/go.mod h1:18ZOQIKpY8NJVqYksKHtTdi31H5itFRjB5/qKTNYzSU=
-golang.org/x/text v0.23.0 h1:D71I7dUrlY+VX0gQShAThNGHFxZ13dGLBHQLVl1mJlY=
-golang.org/x/text v0.23.0/go.mod h1:/BLNzu4aZCJ1+kcD0DNRotWKage4q2rGVAg4o22unh4=
-golang.org/x/time v0.0.0-20180412165947-fbb02b2291d2/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
+golang.org/x/text v0.31.0 h1:aC8ghyu4JhP8VojJ2lEHBnochRno1sgL6nEi9WGFGMM=
+golang.org/x/text v0.31.0/go.mod h1:tKRAlv61yKIjGGHX/4tP1LTbc13YSec1pxVEWXzfoeM=
 golang.org/x/time v0.0.0-20181108054448-85acf8d2951c/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20190308202827-9d24e82272b4/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20191024005414-555d28b269f0/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20200416051211-89c76fbcd5d1/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
-golang.org/x/time v0.9.0 h1:EsRrnYcQiGH+5FfbgvV4AP7qEZstoyrHB0DzarOQ4ZY=
-golang.org/x/time v0.9.0/go.mod h1:3BpzKBy/shNhVucY/MWOyx10tF3SFh9QdLuxbVysPQM=
+golang.org/x/time v0.12.0 h1:ScB/8o8olJvc+CQPWrK3fPZNfh7qgwCrY0zJmoEQLSE=
+golang.org/x/time v0.12.0/go.mod h1:CDIdPxbZBQxdj6cxyCIdrNogrJKMJ7pr37NYpMcMDSg=
 golang.org/x/tools v0.0.0-20180828015842-6cd1fcedba52/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20180917221912-90fa682c2a6e/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
-golang.org/x/tools v0.0.0-20181030000716-a0a13e073c7b/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
-golang.org/x/tools v0.0.0-20181030221726-6c7e314b6563/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20190114222345-bf090417da8b/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20190226205152-f727befe758c/go.mod h1:9Yl7xja0Znq3iFh3HoIrodX9oNMXvdceNzlUR8zjMvY=
 golang.org/x/tools v0.0.0-20190311212946-11955173bddd/go.mod h1:LCzVGOaR6xXOjkQ3onu1FJEFr0SW1gC7cKk1uF8kGRs=
@@ -1575,14 +1456,11 @@ golang.org/x/tools v0.1.1/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
 golang.org/x/tools v0.1.5/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
 golang.org/x/tools v0.1.12/go.mod h1:hNGJHUnrk76NpqgfD5Aqm5Crs+Hm0VOH/i9J2+nxYbc=
 golang.org/x/tools v0.6.0/go.mod h1:Xwgl3UAJ/d3gWutnCtw505GrjyAbvKui8lOU390QaIU=
-golang.org/x/tools v0.31.0 h1:0EedkvKDbh+qistFTd0Bcwe/YLh4vHwWEkiI0toFIBU=
-golang.org/x/tools v0.31.0/go.mod h1:naFTU+Cev749tSJRXJlna0T3WxKvb1kWEx15xA4SdmQ=
+golang.org/x/tools v0.38.0 h1:Hx2Xv8hISq8Lm16jvBZ2VQf+RLmbd7wVUsALibYI/IQ=
+golang.org/x/tools v0.38.0/go.mod h1:yEsQ/d/YK8cjh0L6rZlY8tgtlKiBNTL14pGDJPJpYQs=
 golang.org/x/xerrors v0.0.0-20190212162355-a5947ffaace3/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 gonum.org/v1/gonum v0.15.1 h1:FNy7N6OUZVUaWG9pTiD+jlhdQ3lMP+/LcTpJ6+a8sQ0=
 gonum.org/v1/gonum v0.15.1/go.mod h1:eZTZuRFrzu5pcyjN5wJhcIhnUdNijYxX1T2IcrOGY0o=
-google.golang.org/api v0.0.0-20180910000450-7ca32eb868bf/go.mod h1:4mhQ8q/RsB7i+udVvVy5NUi08OU8ZlA0gRVgrF7VFY0=
-google.golang.org/api v0.0.0-20181030000543-1d582fd0359e/go.mod h1:4mhQ8q/RsB7i+udVvVy5NUi08OU8ZlA0gRVgrF7VFY0=
-google.golang.org/api v0.1.0/go.mod h1:UGEZY7KEX120AnNLIHFMKIo4obdJhkp2tPbaPlQx13Y=
 google.golang.org/api v0.3.1/go.mod h1:6wY9I6uQWHQ8EM57III9mq/AjF+i8G65rmVagqKMtkk=
 google.golang.org/api v0.4.0/go.mod h1:8k5glujaEP+g9n7WNsDg8QP6cUVNI86fCNMcbazEtwE=
 google.golang.org/api v0.7.0/go.mod h1:WtwebWUNSVBH/HAw79HIFXZNqEvBhG+Ra+ax0hx3E3M=
@@ -1604,19 +1482,13 @@ google.golang.org/api v0.35.0/go.mod h1:/XrVsuzM0rZmrsbjJutiuftIzeuTQcEeaYcSk/mQ
 google.golang.org/api v0.36.0/go.mod h1:+z5ficQTmoYpPn8LCUNVpK5I7hwkpjbcgqA7I34qYtE=
 google.golang.org/api v0.40.0/go.mod h1:fYKFpnQN0DsDSKRVRcQSDQNtqWPfM9i+zNPxepjRCQ8=
 google.golang.org/appengine v1.1.0/go.mod h1:EbEs0AVv82hx2wNQdGPgUI5lhzA/G0D9YwlJXL52JkM=
-google.golang.org/appengine v1.2.0/go.mod h1:xpcJRLb0r/rnEns0DIKYYv+WjYCduHsrkT7/EB5XEv4=
-google.golang.org/appengine v1.3.0/go.mod h1:xpcJRLb0r/rnEns0DIKYYv+WjYCduHsrkT7/EB5XEv4=
 google.golang.org/appengine v1.4.0/go.mod h1:xpcJRLb0r/rnEns0DIKYYv+WjYCduHsrkT7/EB5XEv4=
 google.golang.org/appengine v1.5.0/go.mod h1:xpcJRLb0r/rnEns0DIKYYv+WjYCduHsrkT7/EB5XEv4=
 google.golang.org/appengine v1.6.1/go.mod h1:i06prIuMbXzDqacNJfV5OdTW448YApPu5ww/cMBSeb0=
 google.golang.org/appengine v1.6.5/go.mod h1:8WjMMxjGQR8xUklV/ARdw2HLXBOI7O7uCIDZVag1xfc=
 google.golang.org/appengine v1.6.6/go.mod h1:8WjMMxjGQR8xUklV/ARdw2HLXBOI7O7uCIDZVag1xfc=
 google.golang.org/appengine v1.6.7/go.mod h1:8WjMMxjGQR8xUklV/ARdw2HLXBOI7O7uCIDZVag1xfc=
 google.golang.org/genproto v0.0.0-20180817151627-c66870c02cf8/go.mod h1:JiN7NxoALGmiZfu7CAH4rXhgtRTLTxftemlI0sWmxmc=
-google.golang.org/genproto v0.0.0-20180831171423-11092d34479b/go.mod h1:JiN7NxoALGmiZfu7CAH4rXhgtRTLTxftemlI0sWmxmc=
-google.golang.org/genproto v0.0.0-20181029155118-b69ba1387ce2/go.mod h1:JiN7NxoALGmiZfu7CAH4rXhgtRTLTxftemlI0sWmxmc=
-google.golang.org/genproto v0.0.0-20181202183823-bd91e49a0898/go.mod h1:7Ep/1NZk928CDR8SjdVbjWNpdIf6nzjE3BTgJDr2Atg=
-google.golang.org/genproto v0.0.0-20190306203927-b5d61aea6440/go.mod h1:VzzqZJRnGkLBvHegQrXjBqPurQTc5/KpmUdxsrq26oE=
 google.golang.org/genproto v0.0.0-20190307195333-5fe7a883aa19/go.mod h1:VzzqZJRnGkLBvHegQrXjBqPurQTc5/KpmUdxsrq26oE=
 google.golang.org/genproto v0.0.0-20190418145605-e7d98fc518a7/go.mod h1:VzzqZJRnGkLBvHegQrXjBqPurQTc5/KpmUdxsrq26oE=
 google.golang.org/genproto v0.0.0-20190425155659-357c62f0e4bb/go.mod h1:VzzqZJRnGkLBvHegQrXjBqPurQTc5/KpmUdxsrq26oE=
@@ -1656,7 +1528,6 @@ google.golang.org/genproto v0.0.0-20210226172003-ab064af71705/go.mod h1:FWY/as6D
 google.golang.org/genproto v0.0.0-20230410155749-daa745c078e1 h1:KpwkzHKEF7B9Zxg18WzOa7djJ+Ha5DzthMyZYQfEn2A=
 google.golang.org/genproto v0.0.0-20230410155749-daa745c078e1/go.mod h1:nKE/iIaLqn2bQwXBg8f1g2Ylh6r5MN5CmZvuzZCgsCU=
 google.golang.org/grpc v1.14.0/go.mod h1:yo6s7OP7yaDglbqo1J04qKzAhqBH6lvTonzMVmEdcZw=
-google.golang.org/grpc v1.16.0/go.mod h1:0JHn/cJsOMiMfNA9+DeHDlAU7KAAB5GDlYFpa9MZMio=
 google.golang.org/grpc v1.17.0/go.mod h1:6QZJwpn2B+Zp71q/5VxRsJ6NXXVCE5NRUHRo+f3cWCs=
 google.golang.org/grpc v1.19.0/go.mod h1:mqu4LbDTu4XGKhr4mRzUsmM4RtVoemTSY81AxZiDr8c=
 google.golang.org/grpc v1.20.1/go.mod h1:10oTOabMzJvdu6/UiuZezV6QK5dSlG84ov/aaiqXj38=
@@ -1689,8 +1560,8 @@ google.golang.org/protobuf v1.23.0/go.mod h1:EGpADcykh3NcUnDUJcl1+ZksZNG86OlYog2
 google.golang.org/protobuf v1.23.1-0.20200526195155-81db48ad09cc/go.mod h1:EGpADcykh3NcUnDUJcl1+ZksZNG86OlYog2l/sGQquU=
 google.golang.org/protobuf v1.24.0/go.mod h1:r/3tXBNzIEhYS9I1OUVjXDlt8tc493IdKGjtUeSXeh4=
 google.golang.org/protobuf v1.25.0/go.mod h1:9JNX74DMeImyA3h4bdi1ymwjUzf21/xIlbajtzgsN7c=
-google.golang.org/protobuf v1.36.4 h1:6A3ZDJHn/eNqc1i+IdefRzy/9PokBTPvcqMySR7NNIM=
-google.golang.org/protobuf v1.36.4/go.mod h1:9fA7Ob0pmnwhb644+1+CVWFRbNajQ6iRojtC/QF5bRE=
+google.golang.org/protobuf v1.36.6 h1:z1NpPI8ku2WgiWnf+t9wTPsn6eP1L7ksHUlkfLvd9xY=
+google.golang.org/protobuf v1.36.6/go.mod h1:jduwjTPXsFjZGTmRluh+L6NjiWu7pchiJ2/5YcXBHnY=
 gopkg.in/alecthomas/kingpin.v2 v2.2.6/go.mod h1:FMv+mEhP44yOT+4EoQTLFTRgOQ1FBLkstjWtayDeSgw=
 gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
 gopkg.in/check.v1 v1.0.0-20180628173108-788fd7840127/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
@@ -1699,7 +1570,6 @@ gopkg.in/check.v1 v1.0.0-20201130134442-10cb98267c6c h1:Hei/4ADfdWqJk1ZMxUNpqntN
 gopkg.in/check.v1 v1.0.0-20201130134442-10cb98267c6c/go.mod h1:JHkPIbrfpd72SG/EVd6muEfDQjcINNoR0C8j2r3qZ4Q=
 gopkg.in/errgo.v2 v2.1.0/go.mod h1:hNsd1EY+bozCKY1Ytp96fpM3vjJbqLJn88ws8XvfDNI=
 gopkg.in/fsnotify.v1 v1.4.7/go.mod h1:Tz8NjZHkW78fSQdbUxIjBTcgA1z1m8ZHf0WmKUhAMys=
-gopkg.in/inf.v0 v0.9.1/go.mod h1:cWUDdTG/fYaXco+Dcufb5Vnc6Gp2YChqWtbxRZE0mXw=
 gopkg.in/natefinch/lumberjack.v2 v2.2.1 h1:bBRl1b0OH9s/DuPhuXpNl+VtCaJXFZ5/uEFST95x9zc=
 gopkg.in/natefinch/lumberjack.v2 v2.2.1/go.mod h1:YD8tP3GAjkrDg1eZH7EGmyESg/lsYskCTPBJVb9jqSc=
 gopkg.in/square/go-jose.v2 v2.5.1 h1:7odma5RETjNHWJnR32wx8t+Io4djHE1PqxCFx3iiZ2w=
@@ -1718,7 +1588,6 @@ gopkg.in/yaml.v3 v3.0.0-20200313102051-9f266ea9e77c/go.mod h1:K4uyk7z7BCEPqu6E+C
 gopkg.in/yaml.v3 v3.0.0-20210107192922-496545a6307b/go.mod h1:K4uyk7z7BCEPqu6E+C64Yfv1cQ7kz7rIZviUmN+EgEM=
 gopkg.in/yaml.v3 v3.0.1 h1:fxVm/GzAzEWqLHuvctI91KS9hhNmmWOoWu0XTYJS7CA=
 gopkg.in/yaml.v3 v3.0.1/go.mod h1:K4uyk7z7BCEPqu6E+C64Yfv1cQ7kz7rIZviUmN+EgEM=
-grpc.go4.org v0.0.0-20170609214715-11d0a25b4919/go.mod h1:77eQGdRu53HpSqPFJFmuJdjuHRquDANNeA4x7B8WQ9o=
 honnef.co/go/tools v0.0.0-20180728063816-88497007e858/go.mod h1:rf3lG4BRIbNafJWhAfAdb/ePZxsR/4RtNHQocxwk9r4=
 honnef.co/go/tools v0.0.0-20190102054323-c2f93a96b099/go.mod h1:rf3lG4BRIbNafJWhAfAdb/ePZxsR/4RtNHQocxwk9r4=
 honnef.co/go/tools v0.0.0-20190106161140-3f1c8253044a/go.mod h1:rf3lG4BRIbNafJWhAfAdb/ePZxsR/4RtNHQocxwk9r4=
@@ -1727,8 +1596,8 @@ honnef.co/go/tools v0.0.0-20190523083050-ea95bdfd59fc/go.mod h1:rf3lG4BRIbNafJWh
 honnef.co/go/tools v0.0.1-2019.2.3/go.mod h1:a3bituU0lyd329TUQxRnasdCoJDkEUEAqEt0JzvZhAg=
 honnef.co/go/tools v0.0.1-2020.1.3/go.mod h1:X/FiERA/W4tHapMX5mGpAtMSVEeEUOyHaw9vFzvIQ3k=
 honnef.co/go/tools v0.0.1-2020.1.4/go.mod h1:X/FiERA/W4tHapMX5mGpAtMSVEeEUOyHaw9vFzvIQ3k=
-lukechampine.com/blake3 v1.3.0 h1:sJ3XhFINmHSrYCgl958hscfIa3bw8x4DqMP3u1YvoYE=
-lukechampine.com/blake3 v1.3.0/go.mod h1:0OFRp7fBtAylGVCO40o87sbupkyIGgbpv1+M1k1LM6k=
+lukechampine.com/blake3 v1.4.1 h1:I3Smz7gso8w4/TunLKec6K2fn+kyKtDxr/xcQEN84Wg=
+lukechampine.com/blake3 v1.4.1/go.mod h1:QFosUxmjB8mnrWFSNwKmvxHpfY72bmD2tQ0kBMM3kwo=
 modernc.org/cc/v4 v4.25.2 h1:T2oH7sZdGvTaie0BRNFbIYsabzCxUQg8nLqCdQ2i0ic=
 modernc.org/cc/v4 v4.25.2/go.mod h1:uVtb5OGqUKpoLWhqwNQo/8LwvoiEBLvZXIQ/SmO6mL0=
 modernc.org/ccgo/v4 v4.25.1 h1:TFSzPrAGmDsdnhT9X2UrcPMI3N/mJ9/X9ykKXwLhDsU=
@@ -1758,9 +1627,5 @@ pgregory.net/rapid v1.1.0/go.mod h1:PY5XlDGj0+V1FCq0o192FdRhpKHGTRIWBgqjDBTrq04=
 rsc.io/binaryregexp v0.2.0/go.mod h1:qTv7/COck+e2FymRvadv62gMdZztPaShugOCi3I+8D8=
 rsc.io/quote/v3 v3.1.0/go.mod h1:yEA65RcK8LyAZtP9Kv3t0HmxON59tX3rD+tICJqUlj0=
 rsc.io/sampler v1.3.0/go.mod h1:T1hPZKmBbMNahiBKFy5HrXp6adAjACjK9JXDnKaTXpA=
-rsc.io/tmplfunc v0.0.3 h1:53XFQh69AfOa8Tw0Jm7t+GV7KZhOi6jzsCzTtKbMvzU=
-rsc.io/tmplfunc v0.0.3/go.mod h1:AG3sTPzElb1Io3Yg4voV9AGZJuleGAwaVRxL9M49PhA=
-sourcegraph.com/sourcegraph/go-diff v0.5.0/go.mod h1:kuch7UrkMzY0X+p9CRK03kfuPQ2zzQcaEFbx8wA8rck=
-sourcegraph.com/sqs/pbtypes v0.0.0-20180604144634-d3ebe8f20ae4/go.mod h1:ketZ/q3QxT9HOBeFhu6RdvsftgpsbFHBF5Cas6cDKZ0=
 zombiezen.com/go/sqlite v0.13.1 h1:qDzxyWWmMtSSEH5qxamqBFmqA2BLSSbtODi3ojaE02o=
 zombiezen.com/go/sqlite v0.13.1/go.mod h1:Ht/5Rg3Ae2hoyh1I7gbWtWAl89CNocfqeb/aAMTkJr4=
```

### ioctl/newcmd/account/accountcreateadd.go
```diff
@@ -94,7 +94,7 @@ func NewAccountCreateAdd(client ioctl.Client) *cobra.Command {
 				}
 			}
 			if err := client.SetAliasAndSave(args[0], addr); err != nil {
-				return errors.Wrapf(err, failToWriteToConfigFile)
+				return errors.Wrap(err, failToWriteToConfigFile)
 			}
 			cmd.Println(fmt.Sprintf(_outputMessage, args[0]))
 			return nil
```

### ioctl/newcmd/alias/aliasimport.go
```diff
@@ -93,7 +93,7 @@ func NewAliasImport(c ioctl.Client) *cobra.Command {
 				message.ImportedNumber++
 			}
 			if err := c.WriteConfig(); err != nil {
-				return errors.Wrapf(err, failToWriteToConfigFile)
+				return errors.Wrap(err, failToWriteToConfigFile)
 			}
 
 			line := fmt.Sprintf("%d/%d aliases imported\nExisted aliases:", message.ImportedNumber, message.TotalNumber)
```
