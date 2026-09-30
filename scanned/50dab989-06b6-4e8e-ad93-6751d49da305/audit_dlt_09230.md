# [?] Merge pull request #6488 from ipfs/fix/dnsaddr-panic

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2019-07-10
Source: https://github.com/ipfs/kubo/commit/93de78883a00b4b3133dee0a7e44fc6fb91b54bc
Type: security-commit

## Details
Merge pull request #6488 from ipfs/fix/dnsaddr-panic

dep: update go-multiaddr-dns

## Patch
### go.mod
```diff
@@ -5,7 +5,6 @@ require (
 	github.com/Kubuxu/gocovmerge v0.0.0-20161216165753-7ecaa51963cd
 	github.com/blang/semver v3.5.1+incompatible
 	github.com/bren2010/proquint v0.0.0-20160323162903-38337c27106d
-	github.com/cenkalti/backoff v2.1.1+incompatible
 	github.com/dustin/go-humanize v1.0.0
 	github.com/elgris/jsondiff v0.0.0-20160530203242-765b5c24c302
 	github.com/fatih/color v1.7.0 // indirect
@@ -29,7 +28,6 @@ require (
 	github.com/ipfs/go-ds-measure v0.0.1
 	github.com/ipfs/go-fs-lock v0.0.1
 	github.com/ipfs/go-ipfs-blockstore v0.0.1
-	github.com/ipfs/go-ipfs-blocksutil v0.0.1
 	github.com/ipfs/go-ipfs-chunker v0.0.1
 	github.com/ipfs/go-ipfs-cmds v0.1.0
 	github.com/ipfs/go-ipfs-config v0.0.6
@@ -91,7 +89,7 @@ require (
 	github.com/mitchellh/go-homedir v1.1.0
 	github.com/mr-tron/base58 v1.1.2
 	github.com/multiformats/go-multiaddr v0.0.4
-	github.com/multiformats/go-multiaddr-dns v0.0.2
+	github.com/multiformats/go-multiaddr-dns v0.0.3
 	github.com/multiformats/go-multiaddr-net v0.0.1
 	github.com/multiformats/go-multibase v0.0.1
 	github.com/multiformats/go-multihash v0.0.5
@@ -112,7 +110,6 @@ require (
 	go4.org v0.0.0-20190313082347-94abd6928b1d // indirect
 	golang.org/x/sync v0.0.0-20190423024810-112230192c58 // indirect
 	golang.org/x/sys v0.0.0-20190626221950-04f50cda93cb
-	google.golang.org/appengine v1.4.0 // indirect
 	gopkg.in/cheggaaa/pb.v1 v1.0.28
 	gotest.tools/gotestsum v0.3.4
 )
```

### go.sum
```diff
@@ -270,8 +270,6 @@ github.com/ipfs/go-ipfs-posinfo v0.0.1 h1:Esoxj+1JgSjX0+ylc0hUmJCOv6V2vFoZiETLR6
 github.com/ipfs/go-ipfs-posinfo v0.0.1/go.mod h1:SwyeVP+jCwiDu0C313l/8jg6ZxM0qqtlt2a0vILTc1A=
 github.com/ipfs/go-ipfs-pq v0.0.1 h1:zgUotX8dcAB/w/HidJh1zzc1yFq6Vm8J7T2F4itj/RU=
 github.com/ipfs/go-ipfs-pq v0.0.1/go.mod h1:LWIqQpqfRG3fNc5XsnIhz/wQ2XXGyugQwls7BgUmUfY=
-github.com/ipfs/go-ipfs-provider v0.1.0 h1:lYSVVxWpL0KJw1PLj3+DAn0zuVfc+z93wzUXS09ZjZk=
-github.com/ipfs/go-ipfs-provider v0.1.0/go.mod h1:gzVZZXC4zhr2r+MkNR21/+FS54oc7VfTKtDT2mdDxD8=
 github.com/ipfs/go-ipfs-provider v0.1.1 h1:nsC6oWr6bDJ4H7pZfZJqAk6oXaHsrqnwhpQIqTdSDic=
 github.com/ipfs/go-ipfs-provider v0.1.1/go.mod h1:gzVZZXC4zhr2r+MkNR21/+FS54oc7VfTKtDT2mdDxD8=
 github.com/ipfs/go-ipfs-routing v0.0.1/go.mod h1:k76lf20iKFxQTjcJokbPM9iBXVXVZhcOwc360N4nuKs=
@@ -620,6 +618,8 @@ github.com/multiformats/go-multiaddr v0.0.4/go.mod h1:xKVEak1K9cS1VdmPZW3LSIb6lg
 github.com/multiformats/go-multiaddr-dns v0.0.1/go.mod h1:9kWcqw/Pj6FwxAwW38n/9403szc57zJPs45fmnznu3Q=
 github.com/multiformats/go-multiaddr-dns v0.0.2 h1:/Bbsgsy3R6e3jf2qBahzNHzww6usYaZ0NhNH3sqdFS8=
 github.com/multiformats/go-multiaddr-dns v0.0.2/go.mod h1:9kWcqw/Pj6FwxAwW38n/9403szc57zJPs45fmnznu3Q=
+github.com/multiformats/go-multiaddr-dns v0.0.3 h1:P19q/k9jwmtgh+qXFkKfgFM7rCg/9l5AVqh7VNxSXhs=
+github.com/multiformats/go-multiaddr-dns v0.0.3/go.mod h1:9kWcqw/Pj6FwxAwW38n/9403szc57zJPs45fmnznu3Q=
 github.com/multiformats/go-multiaddr-fmt v0.0.1 h1:5YjeOIzbX8OTKVaN72aOzGIYW7PnrZrnkDyOfAWRSMA=
 github.com/multiformats/go-multiaddr-fmt v0.0.1/go.mod h1:aBYjqL4T/7j4Qx+R73XSv/8JsgnRFlf0w2KGLCmXl3Q=
 github.com/multiformats/go-multiaddr-net v0.0.1 h1:76O59E3FavvHqNg7jvzWzsPSW5JSi/ek0E4eiDVbg9g=
```
