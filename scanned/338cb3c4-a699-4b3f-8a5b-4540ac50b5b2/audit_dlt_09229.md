# [?] fix: fix dnsaddr panic

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2019-07-10
Source: https://github.com/ipfs/kubo/commit/50a20ced60ce4f80a2eeb0ff006f38e7e015c52c
Type: security-commit

## Details
fix: fix dnsaddr panic

Cherry-picks https://github.com/ipfs/go-ipfs/pull/6488

## Patch
### go.mod
```diff
@@ -102,7 +102,7 @@ require (
 	github.com/mitchellh/go-homedir v1.1.0
 	github.com/mr-tron/base58 v1.1.2
 	github.com/multiformats/go-multiaddr v0.0.4
-	github.com/multiformats/go-multiaddr-dns v0.0.2
+	github.com/multiformats/go-multiaddr-dns v0.0.3
 	github.com/multiformats/go-multiaddr-net v0.0.1
 	github.com/multiformats/go-multibase v0.0.1
 	github.com/multiformats/go-multihash v0.0.5
```

### go.sum
```diff
@@ -654,6 +654,8 @@ github.com/multiformats/go-multiaddr v0.0.4/go.mod h1:xKVEak1K9cS1VdmPZW3LSIb6lg
 github.com/multiformats/go-multiaddr-dns v0.0.1/go.mod h1:9kWcqw/Pj6FwxAwW38n/9403szc57zJPs45fmnznu3Q=
 github.com/multiformats/go-multiaddr-dns v0.0.2 h1:/Bbsgsy3R6e3jf2qBahzNHzww6usYaZ0NhNH3sqdFS8=
 github.com/multiformats/go-multiaddr-dns v0.0.2/go.mod h1:9kWcqw/Pj6FwxAwW38n/9403szc57zJPs45fmnznu3Q=
+github.com/multiformats/go-multiaddr-dns v0.0.3 h1:P19q/k9jwmtgh+qXFkKfgFM7rCg/9l5AVqh7VNxSXhs=
+github.com/multiformats/go-multiaddr-dns v0.0.3/go.mod h1:9kWcqw/Pj6FwxAwW38n/9403szc57zJPs45fmnznu3Q=
 github.com/multiformats/go-multiaddr-net v0.0.1 h1:76O59E3FavvHqNg7jvzWzsPSW5JSi/ek0E4eiDVbg9g=
 github.com/multiformats/go-multiaddr-net v0.0.1/go.mod h1:nw6HSxNmCIQH27XPGBuX+d1tnvM7ihcFwHMSstNAVUU=
 github.com/multiformats/go-multibase v0.0.1 h1:PN9/v21eLywrFWdFNsFKaU04kLJzuYzmrJR+ubhT9qA=
```
