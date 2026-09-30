# [?] reduce vulnerabilities (#2749)

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygon/zkevm-node
Published: 2023-11-03
Source: https://github.com/0xPolygon/zkevm-node/commit/607f3435498fcadb6e5cfbd662b260ebcd5a885b
Type: security-commit

## Details
reduce vulnerabilities (#2749)

## Patch
### Dockerfile
```diff
@@ -12,7 +12,7 @@ RUN cd /src/db && packr2
 RUN cd /src && make build
 
 # CONTAINER FOR RUNNING BINARY
-FROM alpine:3.18.0
+FROM alpine:3.18.4
 COPY --from=build /src/dist/zkevm-node /app/zkevm-node
 COPY --from=build /src/config/environments/testnet/node.config.toml /app/example.config.toml
 RUN apk update && apk add postgresql15-client
```

### go.mod
```diff
@@ -56,7 +56,7 @@ require (
 	github.com/cockroachdb/pebble v0.0.0-20230906160148-46873a6a7a06 // indirect
 	github.com/cockroachdb/redact v1.1.3 // indirect
 	github.com/consensys/bavard v0.1.13 // indirect
-	github.com/consensys/gnark-crypto v0.10.0 // indirect
+	github.com/consensys/gnark-crypto v0.12.0 // indirect
 	github.com/cpuguy83/go-md2man/v2 v2.0.2 // indirect
 	github.com/crate-crypto/go-kzg-4844 v0.3.0 // indirect
 	github.com/cyphar/filepath-securejoin v0.2.4 // indirect
```

### go.sum
```diff
@@ -137,8 +137,8 @@ github.com/cockroachdb/redact v1.1.3/go.mod h1:BVNblN9mBWFyMyqK1k3AAiSxhvhfK2oOZ
 github.com/codegangsta/inject v0.0.0-20150114235600-33e0aa1cb7c0/go.mod h1:4Zcjuz89kmFXt9morQgcfYZAYZ5n8WHjt81YYWIwtTM=
 github.com/consensys/bavard v0.1.13 h1:oLhMLOFGTLdlda/kma4VOJazblc7IM5y5QPd2A/YjhQ=
 github.com/consensys/bavard v0.1.13/go.mod h1:9ItSMtA/dXMAiL7BG6bqW2m3NdSEObYWoH223nGHukI=
-github.com/consensys/gnark-crypto v0.10.0 h1:zRh22SR7o4K35SoNqouS9J/TKHTyU2QWaj5ldehyXtA=
-github.com/consensys/gnark-crypto v0.10.0/go.mod h1:Iq/P3HHl0ElSjsg2E1gsMwhAyxnxoKK5nVyZKd+/KhU=
+github.com/consensys/gnark-crypto v0.12.0 h1:1OnSpOykNkUIBIBJKdhwy2p0JlW5o+Az02ICzZmvvdg=
+github.com/consensys/gnark-crypto v0.12.0/go.mod h1:v2Gy7L/4ZRosZ7Ivs+9SfUDr0f5UlG+EM5t7MPHiLuY=
 github.com/containerd/continuity v0.0.0-20191214063359-1097c8bae83b h1:pik3LX++5O3UiNWv45wfP/WT81l7ukBJzd3uUiifbSU=
 github.com/containerd/continuity v0.0.0-20191214063359-1097c8bae83b/go.mod h1:Dq467ZllaHgAtVp4p1xUQWBrFXR9s/wyoTpG8zOJGkY=
 github.com/coreos/etcd v3.3.10+incompatible/go.mod h1:uF7uidLiAD3TWHmW31ZFd/JWoc32PjwdhPthX9715RE=
```
