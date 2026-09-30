# [?] Fix Pubsub Panic In Handling Dead Peers (#10976)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2022-07-04
Source: https://github.com/OffchainLabs/prysm/commit/0ed5007d2e51874f158d4bc8dbd632b1b547b3d7
Type: security-commit

## Details
Fix Pubsub Panic In Handling Dead Peers (#10976)

* fix

* fix it

Co-authored-by: prylabs-bulldozer[bot] <58059840+prylabs-bulldozer[bot]@users.noreply.github.com>

## Patch
### beacon-chain/sync/BUILD.bazel
```diff
@@ -104,7 +104,6 @@ go_library(
         "@com_github_kevinms_leakybucket_go//:go_default_library",
         "@com_github_libp2p_go_libp2p_core//:go_default_library",
         "@com_github_libp2p_go_libp2p_core//host:go_default_library",
-        "@com_github_libp2p_go_libp2p_core//mux:go_default_library",
         "@com_github_libp2p_go_libp2p_core//network:go_default_library",
         "@com_github_libp2p_go_libp2p_core//peer:go_default_library",
         "@com_github_libp2p_go_libp2p_core//protocol:go_default_library",
@@ -215,7 +214,6 @@ go_test(
         "@com_github_golang_snappy//:go_default_library",
         "@com_github_kevinms_leakybucket_go//:go_default_library",
         "@com_github_libp2p_go_libp2p_core//:go_default_library",
-        "@com_github_libp2p_go_libp2p_core//mux:go_default_library",
         "@com_github_libp2p_go_libp2p_core//network:go_default_library",
         "@com_github_libp2p_go_libp2p_core//peer:go_default_library",
         "@com_github_libp2p_go_libp2p_core//protocol:go_default_library",
```

### beacon-chain/sync/error.go
```diff
@@ -5,7 +5,6 @@ import (
 	"errors"
 
 	libp2pcore "github.com/libp2p/go-libp2p-core"
-	"github.com/libp2p/go-libp2p-core/mux"
 	"github.com/libp2p/go-libp2p-core/network"
 	"github.com/prysmaticlabs/prysm/beacon-chain/p2p"
 	"github.com/prysmaticlabs/prysm/beacon-chain/p2p/encoder"
@@ -95,7 +94,7 @@ func readStatusCodeNoDeadline(stream network.Stream, encoding encoder.NetworkEnc
 func isValidStreamError(err error) bool {
 	// check the error message itself as well as libp2p doesn't currently
 	// return the correct error type from Close{Read,Write,}.
-	return err != nil && !errors.Is(err, mux.ErrReset) && err.Error() != mux.ErrReset.Error()
+	return err != nil && !errors.Is(err, network.ErrReset) && err.Error() != network.ErrReset.Error()
 }
 
 func closeStream(stream network.Stream, log *logrus.Entry) {
```

### beacon-chain/sync/rpc_send_request_test.go
```diff
@@ -8,7 +8,6 @@ import (
 	"testing"
 	"time"
 
-	"github.com/libp2p/go-libp2p-core/mux"
 	"github.com/libp2p/go-libp2p-core/network"
 	mock "github.com/prysmaticlabs/prysm/beacon-chain/blockchain/testing"
 	"github.com/prysmaticlabs/prysm/beacon-chain/p2p"
@@ -88,7 +87,7 @@ func TestSendRequest_SendBeaconBlocksByRangeRequest(t *testing.T) {
 				wsb, err := wrapper.WrappedSignedBeaconBlock(knownBlocks[i])
 				require.NoError(t, err)
 				err = WriteBlockChunk(stream, chain, p2pProvider.Encoding(), wsb)
-				if err != nil && err.Error() != mux.ErrReset.Error() {
+				if err != nil && err.Error() != network.ErrReset.Error() {
 					require.NoError(t, err)
 				}
 			}
@@ -242,7 +241,7 @@ func TestSendRequest_SendBeaconBlocksByRangeRequest(t *testing.T) {
 				chain := &mock.ChainService{Genesis: time.Now(), ValidatorsRoot: [32]byte{}}
 				wsb, err := wrapper.WrappedSignedBeaconBlock(knownBlocks[i])
 				err = WriteBlockChunk(stream, chain, p2.Encoding(), wsb)
-				if err != nil && err.Error() != mux.ErrReset.Error() {
+				if err != nil && err.Error() != network.ErrReset.Error() {
 					require.NoError(t, err)
 				}
 			}
@@ -287,7 +286,7 @@ func TestSendRequest_SendBeaconBlocksByRangeRequest(t *testing.T) {
 				wsb, err := wrapper.WrappedSignedBeaconBlock(knownBlocks[i])
 				require.NoError(t, err)
 				err = WriteBlockChunk(stream, chain, p2.Encoding(), wsb)
-				if err != nil && err.Error() != mux.ErrReset.Error() {
+				if err != nil && err.Error() != network.ErrReset.Error() {
 					require.NoError(t, err)
 				}
 			}
```

### deps.bzl
```diff
@@ -2189,8 +2189,8 @@ def prysm_deps():
     go_repository(
         name = "com_github_libp2p_go_buffer_pool",
         importpath = "github.com/libp2p/go-buffer-pool",
-        sum = "h1:QNK2iAFa8gjAe1SPz6mHSMuCcjs+X1wlHzeOSqcmlfs=",
-        version = "v0.0.2",
+        sum = "h1:oK4mSFcQz7cTQIfqbe4MIj9gLW+mnanjyFtc6cdF0Y8=",
+        version = "v0.1.0",
     )
     go_repository(
         name = "com_github_libp2p_go_cidranger",
@@ -2286,8 +2286,8 @@ def prysm_deps():
         name = "com_github_libp2p_go_libp2p_pubsub",
         build_file_proto_mode = "disable_global",
         importpath = "github.com/libp2p/go-libp2p-pubsub",
-        sum = "h1:19FI1ziaZWPtlEd6O0bpQuidSUObhoCue3SJPWwkbH4=",
-        version = "v0.7.1-0.20220630043019-ca702289e67f",
+        sum = "h1:Om2zX4v6lQo7CIT99xkCVTSXeSwjfPtzzN3nzQRlApA=",
+        version = "v0.7.1-0.20220701163738-60cf38003244",
     )
     go_repository(
         name = "com_github_libp2p_go_libp2p_quic_transport",
@@ -4512,8 +4512,8 @@ def prysm_deps():
     go_repository(
         name = "org_golang_x_sys",
         importpath = "golang.org/x/sys",
-        sum = "h1:2n253B2r0pYSmEV+UNCQoPfU/FiaizQEK5Gu4Bq4JE8=",
-        version = "v0.0.0-20220627191245-f75cf1eec38b",
+        sum = "h1:xdsejrW/0Wf2diT5CPp3XmKUNbr7Xvw8kYilQ+6qjRY=",
+        version = "v0.0.0-20220702020025-31831981b65f",
     )
     go_repository(
         name = "org_golang_x_term",
```

### go.mod
```diff
@@ -44,7 +44,7 @@ require (
 	github.com/libp2p/go-libp2p v0.20.3
 	github.com/libp2p/go-libp2p-core v0.17.0
 	github.com/libp2p/go-libp2p-peerstore v0.7.0
-	github.com/libp2p/go-libp2p-pubsub v0.7.1-0.20220630043019-ca702289e67f
+	github.com/libp2p/go-libp2p-pubsub v0.7.1-0.20220701163738-60cf38003244
 	github.com/logrusorgru/aurora v2.0.3+incompatible
 	github.com/manifoldco/promptui v0.7.0
 	github.com/minio/highwayhash v1.0.1
@@ -152,7 +152,7 @@ require (
 	github.com/koron/go-ssdp v0.0.3 // indirect
 	github.com/kr/text v0.2.0 // indirect
 	github.com/leodido/go-urn v1.2.1 // indirect
-	github.com/libp2p/go-buffer-pool v0.0.2 // indirect
+	github.com/libp2p/go-buffer-pool v0.1.0 // indirect
 	github.com/libp2p/go-cidranger v1.1.0 // indirect
 	github.com/libp2p/go-eventbus v0.2.1 // indirect
 	github.com/libp2p/go-flow-metrics v0.0.3 // indirect
@@ -252,7 +252,7 @@ require (
 	github.com/peterh/liner v1.2.0 // indirect
 	github.com/prometheus/tsdb v0.10.0 // indirect
 	github.com/prysmaticlabs/gohashtree v0.0.1-alpha.0.20220303211031-f753e083138c
-	golang.org/x/sys v0.0.0-20220627191245-f75cf1eec38b // indirect
+	golang.org/x/sys v0.0.0-20220702020025-31831981b65f // indirect
 	google.golang.org/api v0.34.0 // indirect
 	google.golang.org/appengine v1.6.7 // indirect
 	k8s.io/klog/v2 v2.3.0 // indirect
```

### go.sum
```diff
@@ -747,8 +747,9 @@ github.com/leodido/go-urn v1.2.1 h1:BqpAaACuzVSgi/VLzGZIobT2z4v53pjosyNd9Yv6n/w=
 github.com/leodido/go-urn v1.2.1/go.mod h1:zt4jvISO2HfUBqxjfIshjdMTYS56ZS/qv49ictyFfxY=
 github.com/lib/pq v1.0.0/go.mod h1:5WUZQaWbwv1U+lTReE5YruASi9Al49XbQIvNi/34Woo=
 github.com/libp2p/go-buffer-pool v0.0.1/go.mod h1:xtyIz9PMobb13WaxR6Zo1Pd1zXJKYg0a8KiIvDp3TzQ=
-github.com/libp2p/go-buffer-pool v0.0.2 h1:QNK2iAFa8gjAe1SPz6mHSMuCcjs+X1wlHzeOSqcmlfs=
 github.com/libp2p/go-buffer-pool v0.0.2/go.mod h1:MvaB6xw5vOrDl8rYZGLFdKAuk/hRoRZd1Vi32+RXyFM=
+github.com/libp2p/go-buffer-pool v0.1.0 h1:oK4mSFcQz7cTQIfqbe4MIj9gLW+mnanjyFtc6cdF0Y8=
+github.com/libp2p/go-buffer-pool v0.1.0/go.mod h1:N+vh8gMqimBzdKkSMVuydVDq+UV5QTWy5HSiZacSbPg=
 github.com/libp2p/go-cidranger v1.1.0 h1:ewPN8EZ0dd1LSnrtuwd4709PXVcITVeuwbag38yPW7c=
 github.com/libp2p/go-cidranger v1.1.0/go.mod h1:KWZTfSr+r9qEo9OkI9/SIEeAtw+NNoU0dXIXt15Okic=
 github.com/libp2p/go-conn-security-multistream v0.3.0/go.mod h1:EEP47t4fw/bTelVmEzIDqSe69hO/ip52xBEhZMLWAHM=
@@ -782,8 +783,8 @@ github.com/libp2p/go-libp2p-peerstore v0.6.0/go.mod h1:DGEmKdXrcYpK9Jha3sS7MhqYd
 github.com/libp2p/go-libp2p-peerstore v0.7.0 h1:2iIUwok3vtmnWJTZeTeLgnBO6GbkXcwSRwgZHEKrQZs=
 github.com/libp2p/go-libp2p-peerstore v0.7.0/go.mod h1:cdUWTHro83vpg6unCpGUr8qJoX3e93Vy8o97u5ppIM0=
 github.com/libp2p/go-libp2p-pnet v0.2.0/go.mod h1:Qqvq6JH/oMZGwqs3N1Fqhv8NVhrdYcO0BW4wssv21LA=
-github.com/libp2p/go-libp2p-pubsub v0.7.1-0.20220630043019-ca702289e67f h1:19FI1ziaZWPtlEd6O0bpQuidSUObhoCue3SJPWwkbH4=
-github.com/libp2p/go-libp2p-pubsub v0.7.1-0.20220630043019-ca702289e67f/go.mod h1:y+eARQ8AoaWpe0mlz3/uYKdl+GhFOtIxjG5xeek2kbM=
+github.com/libp2p/go-libp2p-pubsub v0.7.1-0.20220701163738-60cf38003244 h1:Om2zX4v6lQo7CIT99xkCVTSXeSwjfPtzzN3nzQRlApA=
+github.com/libp2p/go-libp2p-pubsub v0.7.1-0.20220701163738-60cf38003244/go.mod h1:y+eARQ8AoaWpe0mlz3/uYKdl+GhFOtIxjG5xeek2kbM=
 github.com/libp2p/go-libp2p-quic-transport v0.16.0/go.mod h1:1BXjVMzr+w7EkPfiHkKnwsWjPjtfaNT0q8RS3tGDvEQ=
 github.com/libp2p/go-libp2p-resource-manager v0.3.0 h1:2+cYxUNi33tcydsVLt6K5Fv2E3OTiVeafltecAj15E0=
 github.com/libp2p/go-libp2p-resource-manager v0.3.0/go.mod h1:K+eCkiapf+ey/LADO4TaMpMTP9/Qde/uLlrnRqV4PLQ=
@@ -1696,8 +1697,8 @@ golang.org/x/sys v0.0.0-20211216021012-1d35b9e2eb4e/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20220114195835-da31bd327af9/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220412211240-33da011f77ad/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220422013727-9388b58f7150/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/sys v0.0.0-20220627191245-f75cf1eec38b h1:2n253B2r0pYSmEV+UNCQoPfU/FiaizQEK5Gu4Bq4JE8=
-golang.org/x/sys v0.0.0-20220627191245-f75cf1eec38b/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.0.0-20220702020025-31831981b65f h1:xdsejrW/0Wf2diT5CPp3XmKUNbr7Xvw8kYilQ+6qjRY=
+golang.org/x/sys v0.0.0-20220702020025-31831981b65f/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/term v0.0.0-20201117132131-f5c789dd3221/go.mod h1:Nr5EML6q2oocZ2LXRh80K7BxOlk5/8JxuGnuhpl+muw=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211 h1:JGgROgKl9N8DuW20oFS5gxc+lE67/N3FcwmBPMe7ArY=
```
