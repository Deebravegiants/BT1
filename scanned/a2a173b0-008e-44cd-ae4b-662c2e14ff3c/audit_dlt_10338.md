# [?] Update geth dependency to include data race fixes (#291)

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2025-06-10
Source: https://github.com/0xsoniclabs/sonic/commit/3b58d61d04210f438888c21dc37b5de5a9e67eed
Type: security-commit

## Details
Update geth dependency to include data race fixes (#291)

## Patch
### go.mod
```diff
@@ -126,7 +126,7 @@ require (
 	rsc.io/tmplfunc v0.0.3 // indirect
 )
 
-replace github.com/ethereum/go-ethereum => github.com/0xsoniclabs/go-ethereum v0.0.0-20250403075908-a6b1c7063681
+replace github.com/ethereum/go-ethereum => github.com/0xsoniclabs/go-ethereum v0.0.0-20250610102820-1c3a8f11446c
 
 replace github.com/Fantom-foundation/lachesis-base => github.com/Fantom-foundation/lachesis-base-sonic v0.0.0-20250212122819-abaef8bb9abb
 
```

### go.sum
```diff
@@ -1,7 +1,7 @@
 github.com/0xsoniclabs/carmen/go v0.0.0-20250530111616-fabde4233b62 h1:NF+A6zk8FYDuDk9aTVtzn7/e8kj+LERtyt+cfcHz+vM=
 github.com/0xsoniclabs/carmen/go v0.0.0-20250530111616-fabde4233b62/go.mod h1:s161Ju9dIK9gZ982wBx2WaCNN5Hv4OjC6YyoftKKF48=
-github.com/0xsoniclabs/go-ethereum v0.0.0-20250403075908-a6b1c7063681 h1:0cGG6PL3gPMHUzlog9ivCQJ6L3Lrmm0H+Jn3h2ke7zo=
-github.com/0xsoniclabs/go-ethereum v0.0.0-20250403075908-a6b1c7063681/go.mod h1:neQD30i5v+/u41EUK4C9lFAnjefSWD6xhbdGI/rg6YQ=
+github.com/0xsoniclabs/go-ethereum v0.0.0-20250610102820-1c3a8f11446c h1:AkC2+PPkaTQ/wiVHskadK0oYHitALhGicQRFPXL6vmQ=
+github.com/0xsoniclabs/go-ethereum v0.0.0-20250610102820-1c3a8f11446c/go.mod h1:neQD30i5v+/u41EUK4C9lFAnjefSWD6xhbdGI/rg6YQ=
 github.com/0xsoniclabs/tosca v0.0.0-20250414093812-91b42e73396f h1:Cqn4e6+R7zbQxZuzOkjvO1PTHCXz/wbR9ZCKTf69uvk=
 github.com/0xsoniclabs/tosca v0.0.0-20250414093812-91b42e73396f/go.mod h1:LujnkwOuuV44CNdNI/YI8bFb8YGKSq4Imof7n4sxcfc=
 github.com/DataDog/zstd v1.5.6 h1:LbEglqepa/ipmmQJUDnSsfvA8e8IStVcGaFWDuxvGOY=
```
