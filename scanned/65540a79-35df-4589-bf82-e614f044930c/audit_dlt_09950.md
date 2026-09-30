# [?] fix: prevent goleveldb panic on large genesis files(#1661)

## Summary
Severity: Unknown
Chain: Kava
Component: Kava-Labs/kava
Published: 2023-08-16
Source: https://github.com/Kava-Labs/kava/commit/47416b3d1af6dfd31bab479d78b24cdbb677be31
Type: security-commit

## Details
fix: prevent goleveldb panic on large genesis files(#1661)

Backport of #1631

## Patch
### CHANGELOG.md
```diff
@@ -103,6 +103,9 @@ Ref: https://keepachangelog.com/en/1.0.0/
 ### Bug Fixes
 
 - (x/incentive) [#1550] Fix validation on genesis reward accumulation time.
+- (deps) [#1622] Bump tm-db to v0.6.7-kava.3 to return rocksdb open error
+- (deps) [#1631] Bump cometbft to v0.34.27-kava.0 to avoid goleveldb panic on large
+  genesis files.
 
 ## [v0.16.1]
 
@@ -275,6 +278,7 @@ the [changelog](https://github.com/cosmos/cosmos-sdk/blob/v0.38.4/CHANGELOG.md).
 
 [#1655]: https://github.com/Kava-Labs/kava/pull/1655
 [#1624]: https://github.com/Kava-Labs/kava/pull/1624
+[#1631]: https://github.com/Kava-Labs/kava/pull/1631
 [#1622]: https://github.com/Kava-Labs/kava/pull/1622
 [#1614]: https://github.com/Kava-Labs/kava/pull/1614
 [#1610]: https://github.com/Kava-Labs/kava/pull/1610
```

### go.mod
```diff
@@ -214,7 +214,7 @@ replace (
 	// Downgraded to avoid bugs in following commits which causes "version does not exist" errors
 	github.com/syndtr/goleveldb => github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7
 	// Use cometbft fork of tendermint
-	github.com/tendermint/tendermint => github.com/cometbft/cometbft v0.34.27
+	github.com/tendermint/tendermint => github.com/kava-labs/cometbft v0.34.27-kava.0
 	// Indirect dependencies still use tendermint/tm-db
 	github.com/tendermint/tm-db => github.com/kava-labs/tm-db v0.6.7-kava.3
 )
```

### go.sum
```diff
@@ -354,8 +354,6 @@ github.com/codahale/hdrhistogram v0.0.0-20161010025455-3a0bb77429bd/go.mod h1:sE
 github.com/coinbase/kryptology v1.8.0/go.mod h1:RYXOAPdzOGUe3qlSFkMGn58i3xUA8hmxYHksuq+8ciI=
 github.com/coinbase/rosetta-sdk-go v0.7.9 h1:lqllBjMnazTjIqYrOGv8h8jxjg9+hJazIGZr9ZvoCcA=
 github.com/coinbase/rosetta-sdk-go v0.7.9/go.mod h1:0/knutI7XGVqXmmH4OQD8OckFrbQ8yMsUZTG7FXCR2M=
-github.com/cometbft/cometbft v0.34.27 h1:ri6BvmwjWR0gurYjywcBqRe4bbwc3QVs9KRcCzgh/J0=
-github.com/cometbft/cometbft v0.34.27/go.mod h1:BcCbhKv7ieM0KEddnYXvQZR+pZykTKReJJYf7YC7qhw=
 github.com/confio/ics23/go v0.9.0 h1:cWs+wdbS2KRPZezoaaj+qBleXgUk5WOQFMP3CQFGTr4=
 github.com/confio/ics23/go v0.9.0/go.mod h1:4LPZ2NYqnYIVRklaozjNR1FScgDJ2s5Xrp+e/mYVRak=
 github.com/consensys/bavard v0.1.8-0.20210406032232-f3452dc9b572/go.mod h1:Bpd0/3mZuaj6Sj+PqrmIquiOKy397AKGThQPaGzNXAQ=
@@ -802,6 +800,8 @@ github.com/julienschmidt/httprouter v1.3.0/go.mod h1:JR6WtHb+2LUe8TCKY3cZOxFyyO8
 github.com/jung-kurt/gofpdf v1.0.3-0.20190309125859-24315acbbda5/go.mod h1:7Id9E/uU8ce6rXgefFLlgrJj/GYY22cpxn+r32jIOes=
 github.com/jwilder/encoding v0.0.0-20170811194829-b4e1701a28ef/go.mod h1:Ct9fl0F6iIOGgxJ5npU/IUOhOhqlVrGjyIZc8/MagT0=
 github.com/karalabe/usb v0.0.2/go.mod h1:Od972xHfMJowv7NGVDiWVxk2zxnWgjLlJzE+F4F7AGU=
+github.com/kava-labs/cometbft v0.34.27-kava.0 h1:FUEGRkF3xtrJH+h9A5G4eA2skf7QaNoOCPaoVqHkh8k=
+github.com/kava-labs/cometbft v0.34.27-kava.0/go.mod h1:BcCbhKv7ieM0KEddnYXvQZR+pZykTKReJJYf7YC7qhw=
 github.com/kava-labs/cometbft-db v0.7.0-rocksdb-v7.9.2-kava.1 h1:EZnZAkZ+dqK+1OM4AK+e6wYH8a5xuyg4yFTR4Ez3AXk=
 github.com/kava-labs/cometbft-db v0.7.0-rocksdb-v7.9.2-kava.1/go.mod h1:mI/4J4IxRzPrXvMiwefrt0fucGwaQ5Hm9IKS7HnoJeI=
 github.com/kava-labs/cosmos-sdk v0.46.11-kava.1 h1:3VRpm4zf/gQgmpRVd1p99/2P8ZecAu2FVAXHru5caIo=
```
