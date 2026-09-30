# [?] bump solana version: contains race condition fix (#9267)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-05-19
Source: https://github.com/smartcontractkit/ccip/commit/dd0c60bb6d863993da676bda06e5f395b544bb2d
Type: security-commit

## Details
bump solana version: contains race condition fix (#9267)

Co-authored-by: Jordan Krage <jmank88@gmail.com>

## Patch
### core/scripts/go.mod
```diff
@@ -287,7 +287,7 @@ require (
 	github.com/sirupsen/logrus v1.9.0 // indirect
 	github.com/smartcontractkit/chainlink-cosmos v0.4.0 // indirect
 	github.com/smartcontractkit/chainlink-relay v0.1.7-0.20230517200758-40dada2543a1 // indirect
-	github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230516001004-0216997a2508 // indirect
+	github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230518143827-0b7a6e43719c // indirect
 	github.com/smartcontractkit/chainlink-starknet/relayer v0.0.0-20230424184429-bfdf6bddb239 // indirect
 	github.com/smartcontractkit/wsrpc v0.7.2 // indirect
 	github.com/spacemonkeygo/spacelog v0.0.0-20180420211403-2296661a0572 // indirect
```

### core/scripts/go.sum
```diff
@@ -1374,8 +1374,8 @@ github.com/smartcontractkit/chainlink-cosmos v0.4.0 h1:xYLAcJJIm0cyMtYtMaosO45by
 github.com/smartcontractkit/chainlink-cosmos v0.4.0/go.mod h1:938jBqOrhdCq4A8enUiBliiDLBndAXebHIitKsDVqY0=
 github.com/smartcontractkit/chainlink-relay v0.1.7-0.20230517200758-40dada2543a1 h1:/gqM+lMSfoxdNSeruMgEdqA7a/RJuz6l36LPuKoI1EU=
 github.com/smartcontractkit/chainlink-relay v0.1.7-0.20230517200758-40dada2543a1/go.mod h1:f7/HKcJWWFzINrkDDlpKsFaU6D+8D4B4OrQxkkCX4oc=
-github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230516001004-0216997a2508 h1:hsCcqkK7ZgABURMRYbNgRdVbNJv7JJPGlgKJbukjMsk=
-github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230516001004-0216997a2508/go.mod h1:CUmP50gxZsjwEYA7balCV3mhvX0CrR/a01X6jGBZR8I=
+github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230518143827-0b7a6e43719c h1:pM7FH+S92F7Xa/VSfbIs941FDKqSmo9pYeUBWHl1Pq0=
+github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230518143827-0b7a6e43719c/go.mod h1:CUmP50gxZsjwEYA7balCV3mhvX0CrR/a01X6jGBZR8I=
 github.com/smartcontractkit/chainlink-starknet/relayer v0.0.0-20230424184429-bfdf6bddb239 h1:YmYkbdM5YXVV+IWgp+5ctfplMEoXamT0LR0qsnM4eps=
 github.com/smartcontractkit/chainlink-starknet/relayer v0.0.0-20230424184429-bfdf6bddb239/go.mod h1:RZzvRfGjMe4lBOT1H/MRfjnNoyUWOiHlOcHx/BZYg+M=
 github.com/smartcontractkit/libocr v0.0.0-20230413082317-9561d14087cc h1:aSCDAai0Dmbhp/KHTtJnC/EJcaEz4CAO80SKRzRZiQA=
```

### go.mod
```diff
@@ -66,7 +66,7 @@ require (
 	github.com/shopspring/decimal v1.3.1
 	github.com/smartcontractkit/chainlink-cosmos v0.4.0
 	github.com/smartcontractkit/chainlink-relay v0.1.7-0.20230517200758-40dada2543a1
-	github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230516001004-0216997a2508
+	github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230518143827-0b7a6e43719c
 	github.com/smartcontractkit/chainlink-starknet/relayer v0.0.0-20230424184429-bfdf6bddb239
 	github.com/smartcontractkit/libocr v0.0.0-20230413082317-9561d14087cc
 	github.com/smartcontractkit/ocr2keepers v0.6.15
```

### go.sum
```diff
@@ -1388,8 +1388,8 @@ github.com/smartcontractkit/chainlink-cosmos v0.4.0 h1:xYLAcJJIm0cyMtYtMaosO45by
 github.com/smartcontractkit/chainlink-cosmos v0.4.0/go.mod h1:938jBqOrhdCq4A8enUiBliiDLBndAXebHIitKsDVqY0=
 github.com/smartcontractkit/chainlink-relay v0.1.7-0.20230517200758-40dada2543a1 h1:/gqM+lMSfoxdNSeruMgEdqA7a/RJuz6l36LPuKoI1EU=
 github.com/smartcontractkit/chainlink-relay v0.1.7-0.20230517200758-40dada2543a1/go.mod h1:f7/HKcJWWFzINrkDDlpKsFaU6D+8D4B4OrQxkkCX4oc=
-github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230516001004-0216997a2508 h1:hsCcqkK7ZgABURMRYbNgRdVbNJv7JJPGlgKJbukjMsk=
-github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230516001004-0216997a2508/go.mod h1:CUmP50gxZsjwEYA7balCV3mhvX0CrR/a01X6jGBZR8I=
+github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230518143827-0b7a6e43719c h1:pM7FH+S92F7Xa/VSfbIs941FDKqSmo9pYeUBWHl1Pq0=
+github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230518143827-0b7a6e43719c/go.mod h1:CUmP50gxZsjwEYA7balCV3mhvX0CrR/a01X6jGBZR8I=
 github.com/smartcontractkit/chainlink-starknet/relayer v0.0.0-20230424184429-bfdf6bddb239 h1:YmYkbdM5YXVV+IWgp+5ctfplMEoXamT0LR0qsnM4eps=
 github.com/smartcontractkit/chainlink-starknet/relayer v0.0.0-20230424184429-bfdf6bddb239/go.mod h1:RZzvRfGjMe4lBOT1H/MRfjnNoyUWOiHlOcHx/BZYg+M=
 github.com/smartcontractkit/libocr v0.0.0-20230413082317-9561d14087cc h1:aSCDAai0Dmbhp/KHTtJnC/EJcaEz4CAO80SKRzRZiQA=
```

### integration-tests/go.sum
```diff
@@ -1345,7 +1345,7 @@ github.com/smartcontractkit/chainlink-env v0.32.2 h1:4o9TyvseEIGV/MGqkklQKfrsXUI
 github.com/smartcontractkit/chainlink-env v0.32.2/go.mod h1:9c0Czq4a6wZKY20BcoAlK29DnejQIiLo/MwKYtSFnHk=
 github.com/smartcontractkit/chainlink-relay v0.1.7-0.20230517200758-40dada2543a1 h1:/gqM+lMSfoxdNSeruMgEdqA7a/RJuz6l36LPuKoI1EU=
 github.com/smartcontractkit/chainlink-relay v0.1.7-0.20230517200758-40dada2543a1/go.mod h1:f7/HKcJWWFzINrkDDlpKsFaU6D+8D4B4OrQxkkCX4oc=
-github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230516001004-0216997a2508 h1:hsCcqkK7ZgABURMRYbNgRdVbNJv7JJPGlgKJbukjMsk=
+github.com/smartcontractkit/chainlink-solana v1.0.3-0.20230518143827-0b7a6e43719c h1:pM7FH+S92F7Xa/VSfbIs941FDKqSmo9pYeUBWHl1Pq0=
 github.com/smartcontractkit/chainlink-starknet/relayer v0.0.0-20230424184429-bfdf6bddb239 h1:YmYkbdM5YXVV+IWgp+5ctfplMEoXamT0LR0qsnM4eps=
 github.com/smartcontractkit/chainlink-starknet/relayer v0.0.0-20230424184429-bfdf6bddb239/go.mod h1:RZzvRfGjMe4lBOT1H/MRfjnNoyUWOiHlOcHx/BZYg+M=
 github.com/smartcontractkit/chainlink-testing-framework v1.11.6 h1:W5BfxVDRWZ/PepyMUyJqR8w8XcnFbP4aZqL+ha+DiaA=
```
