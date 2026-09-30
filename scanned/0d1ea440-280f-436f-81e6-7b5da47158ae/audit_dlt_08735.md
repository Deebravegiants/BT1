# [?] fix: update da-codec to prevent zstd deadlock (#1237)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2025-09-04
Source: https://github.com/scroll-tech/go-ethereum/commit/afbbad7c909befc1cf723a5e17eabbfe39a1274a
Type: security-commit

## Details
fix: update da-codec to prevent zstd deadlock (#1237)

* fix: update da-codec to prevent zstd deadlock

* chore: auto version bump [bot]

## Patch
### go.mod
```diff
@@ -51,7 +51,7 @@ require (
 	github.com/prometheus/tsdb v0.7.1
 	github.com/rjeczalik/notify v0.9.1
 	github.com/rs/cors v1.7.0
-	github.com/scroll-tech/da-codec v0.1.3-0.20250626091118-58b899494da6
+	github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6
 	github.com/scroll-tech/zktrie v0.8.4
 	github.com/shirou/gopsutil v3.21.11+incompatible
 	github.com/sourcegraph/conc v0.3.0
```

### go.sum
```diff
@@ -396,8 +396,8 @@ github.com/rogpeppe/go-internal v1.10.0/go.mod h1:UQnix2H7Ngw/k4C5ijL5+65zddjncj
 github.com/rs/cors v1.7.0 h1:+88SsELBHx5r+hZ8TCkggzSstaWNbDvThkVK8H6f9ik=
 github.com/rs/cors v1.7.0/go.mod h1:gFx+x8UowdsKA9AchylcLynDq+nNFfI8FkUZdN/jGCU=
 github.com/russross/blackfriday/v2 v2.0.1/go.mod h1:+Rmxgy9KzJVeS9/2gXHxylqXiyQDYRxCVz55jmeOWTM=
-github.com/scroll-tech/da-codec v0.1.3-0.20250626091118-58b899494da6 h1:vb2XLvQwCf+F/ifP6P/lfeiQrHY6+Yb/E3R4KHXLqSE=
-github.com/scroll-tech/da-codec v0.1.3-0.20250626091118-58b899494da6/go.mod h1:Z6kN5u2khPhiqHyk172kGB7o38bH/nj7Ilrb/46wZGg=
+github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6 h1:EiLZgoRfGgF0QzZ1jGSlo60A6W7g9L/8XLWMhwwtKJ0=
+github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6/go.mod h1:Z6kN5u2khPhiqHyk172kGB7o38bH/nj7Ilrb/46wZGg=
 github.com/scroll-tech/zktrie v0.8.4 h1:UagmnZ4Z3ITCk+aUq9NQZJNAwnWl4gSxsLb2Nl7IgRE=
 github.com/scroll-tech/zktrie v0.8.4/go.mod h1:XvNo7vAk8yxNyTjBDj5WIiFzYW4bx/gJ78+NK6Zn6Uk=
 github.com/segmentio/kafka-go v0.1.0/go.mod h1:X6itGqS9L4jDletMsxZ7Dz+JFWxM6JHfPOCvTvk+EJo=
```

### params/version.go
```diff
@@ -24,7 +24,7 @@ import (
 const (
 	VersionMajor = 5         // Major version component of the current release
 	VersionMinor = 9         // Minor version component of the current release
-	VersionPatch = 3         // Patch version component of the current release
+	VersionPatch = 4         // Patch version component of the current release
 	VersionMeta  = "mainnet" // Version metadata to append to the version string
 )
 
```
