# [?] Update common to fix a panic in cre module caused by a malicious workflow overflowing an int32. (#22798)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2026-06-10
Source: https://github.com/smartcontractkit/chainlink/commit/faa7d1b78ba9ca1690f68ec235dd6b791fd959ce
Type: security-commit

## Details
Update common to fix a panic in cre module caused by a malicious workflow overflowing an int32. (#22798)

## Patch
### core/scripts/go.mod
```diff
@@ -43,7 +43,7 @@ require (
 	github.com/smartcontractkit/chain-selectors v1.0.101
 	github.com/smartcontractkit/chainlink-automation v0.8.1
 	github.com/smartcontractkit/chainlink-ccip/chains/evm v0.0.0-20260506144252-c100eabfda74
-	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e
+	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b
 	github.com/smartcontractkit/chainlink-common/keystore v1.2.0
 	github.com/smartcontractkit/chainlink-data-streams v0.1.15-0.20260522094612-5f9f748bd87a
 	github.com/smartcontractkit/chainlink-deployments-framework v0.105.0
```

### core/scripts/go.sum
```diff
@@ -1573,8 +1573,8 @@ github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20260
 github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20260511195239-0f6e1b177fc7/go.mod h1:67YbnoglYD61Pz/jTVCgav9wFq7S35OU8UyQSvPllRw=
 github.com/smartcontractkit/chainlink-ccv v0.0.2-0.20260428133800-3b1484e8b1fd h1:IMopuENFVS63AerRELdfWo6o60UNUidcldJOxJLmk24=
 github.com/smartcontractkit/chainlink-ccv v0.0.2-0.20260428133800-3b1484e8b1fd/go.mod h1:SBN8Urnh5sQvrQRbSo1Nr8coWatHg8LZoPw3R/42sho=
-github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e h1:uTuCrOqBZeYfIl2QG70KuCG7xpubUETFJpHiip5+7FU=
-github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e/go.mod h1:GlEVw7ziizXoMfzl1onNSwansrVBLHhj5gUJlGQpb4I=
+github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b h1:UMQ+MwHI341h+yARqeKmY/cagkB/dH0J34aMoJG00io=
+github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b/go.mod h1:GlEVw7ziizXoMfzl1onNSwansrVBLHhj5gUJlGQpb4I=
 github.com/smartcontractkit/chainlink-common/keystore v1.2.0 h1:1BH/b14CkGjArfzznlioQpIJiynECWVT48JUP9E277U=
 github.com/smartcontractkit/chainlink-common/keystore v1.2.0/go.mod h1:9R/74vN+bJ5PbkOyM/pUy/AeAZaRwYb/k4XPeXcbDio=
 github.com/smartcontractkit/chainlink-common/pkg/chipingress v0.0.11-0.20260601211238-9f526774fef0 h1:NExKM/D0HneOq/N5LGTbkV4VOa0UHCvfTNEb4GqYpto=
```

### deployment/go.mod
```diff
@@ -42,7 +42,7 @@ require (
 	github.com/smartcontractkit/chainlink-ccip/chains/solana v0.0.0-20260415165642-49f23e4d76cc
 	github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20260511195239-0f6e1b177fc7
 	github.com/smartcontractkit/chainlink-ccip/deployment v0.0.0-20260504204047-af9826978b72
-	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e
+	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b
 	github.com/smartcontractkit/chainlink-common/keystore v1.2.0
 	github.com/smartcontractkit/chainlink-data-streams v0.1.15-0.20260522094612-5f9f748bd87a
 	github.com/smartcontractkit/chainlink-deployments-framework v0.105.0
```

### deployment/go.sum
```diff
@@ -1382,8 +1382,8 @@ github.com/smartcontractkit/chainlink-ccv v0.0.2-0.20260428133800-3b1484e8b1fd h
 github.com/smartcontractkit/chainlink-ccv v0.0.2-0.20260428133800-3b1484e8b1fd/go.mod h1:SBN8Urnh5sQvrQRbSo1Nr8coWatHg8LZoPw3R/42sho=
 github.com/smartcontractkit/chainlink-ccv/deployment v0.0.2-0.20260428205321-9ce8f4c44d23 h1:1Rt4HLpwbRN1YtBFcbsxSJYIiUP2wJ11qizevOEeCrs=
 github.com/smartcontractkit/chainlink-ccv/deployment v0.0.2-0.20260428205321-9ce8f4c44d23/go.mod h1:V+wrhuNve+JiFwoBr25d6y0lL1rYSCSJhTFyloL3ueo=
-github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e h1:uTuCrOqBZeYfIl2QG70KuCG7xpubUETFJpHiip5+7FU=
-github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e/go.mod h1:GlEVw7ziizXoMfzl1onNSwansrVBLHhj5gUJlGQpb4I=
+github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b h1:UMQ+MwHI341h+yARqeKmY/cagkB/dH0J34aMoJG00io=
+github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b/go.mod h1:GlEVw7ziizXoMfzl1onNSwansrVBLHhj5gUJlGQpb4I=
 github.com/smartcontractkit/chainlink-common/keystore v1.2.0 h1:1BH/b14CkGjArfzznlioQpIJiynECWVT48JUP9E277U=
 github.com/smartcontractkit/chainlink-common/keystore v1.2.0/go.mod h1:9R/74vN+bJ5PbkOyM/pUy/AeAZaRwYb/k4XPeXcbDio=
 github.com/smartcontractkit/chainlink-common/pkg/chipingress v0.0.11-0.20260601211238-9f526774fef0 h1:NExKM/D0HneOq/N5LGTbkV4VOa0UHCvfTNEb4GqYpto=
```

### go.mod
```diff
@@ -85,7 +85,7 @@ require (
 	github.com/smartcontractkit/chainlink-ccip/chains/solana v0.0.0-20260415165642-49f23e4d76cc
 	github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20260415165642-49f23e4d76cc
 	github.com/smartcontractkit/chainlink-ccv v0.0.2-0.20260428133800-3b1484e8b1fd
-	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e
+	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b
 	github.com/smartcontractkit/chainlink-common/keystore v1.2.0
 	github.com/smartcontractkit/chainlink-common/pkg/chipingress v0.0.11-0.20260601211238-9f526774fef0
 	github.com/smartcontractkit/chainlink-data-streams v0.1.15-0.20260522094612-5f9f748bd87a
```

### go.sum
```diff
@@ -1181,8 +1181,8 @@ github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20260
 github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20260415165642-49f23e4d76cc/go.mod h1:67YbnoglYD61Pz/jTVCgav9wFq7S35OU8UyQSvPllRw=
 github.com/smartcontractkit/chainlink-ccv v0.0.2-0.20260428133800-3b1484e8b1fd h1:IMopuENFVS63AerRELdfWo6o60UNUidcldJOxJLmk24=
 github.com/smartcontractkit/chainlink-ccv v0.0.2-0.20260428133800-3b1484e8b1fd/go.mod h1:SBN8Urnh5sQvrQRbSo1Nr8coWatHg8LZoPw3R/42sho=
-github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e h1:uTuCrOqBZeYfIl2QG70KuCG7xpubUETFJpHiip5+7FU=
-github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e/go.mod h1:GlEVw7ziizXoMfzl1onNSwansrVBLHhj5gUJlGQpb4I=
+github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b h1:UMQ+MwHI341h+yARqeKmY/cagkB/dH0J34aMoJG00io=
+github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b/go.mod h1:GlEVw7ziizXoMfzl1onNSwansrVBLHhj5gUJlGQpb4I=
 github.com/smartcontractkit/chainlink-common/keystore v1.2.0 h1:1BH/b14CkGjArfzznlioQpIJiynECWVT48JUP9E277U=
 github.com/smartcontractkit/chainlink-common/keystore v1.2.0/go.mod h1:9R/74vN+bJ5PbkOyM/pUy/AeAZaRwYb/k4XPeXcbDio=
 github.com/smartcontractkit/chainlink-common/pkg/chipingress v0.0.11-0.20260601211238-9f526774fef0 h1:NExKM/D0HneOq/N5LGTbkV4VOa0UHCvfTNEb4GqYpto=
```

### integration-tests/go.mod
```diff
@@ -29,7 +29,7 @@ require (
 	github.com/smartcontractkit/chainlink-ccip/chains/evm v0.0.0-20260506144252-c100eabfda74
 	github.com/smartcontractkit/chainlink-ccip/chains/solana v0.0.0-20260506144252-c100eabfda74
 	github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20260511195239-0f6e1b177fc7
-	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e
+	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b
 	github.com/smartcontractkit/chainlink-common/keystore v1.2.0
 	github.com/smartcontractkit/chainlink-deployments-framework v0.105.0
 	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260609161557-8ceae53b8ab1
```

### integration-tests/go.sum
```diff
@@ -1367,8 +1367,8 @@ github.com/smartcontractkit/chainlink-ccv v0.0.2-0.20260428133800-3b1484e8b1fd h
 github.com/smartcontractkit/chainlink-ccv v0.0.2-0.20260428133800-3b1484e8b1fd/go.mod h1:SBN8Urnh5sQvrQRbSo1Nr8coWatHg8LZoPw3R/42sho=
 github.com/smartcontractkit/chainlink-ccv/deployment v0.0.2-0.20260428205321-9ce8f4c44d23 h1:1Rt4HLpwbRN1YtBFcbsxSJYIiUP2wJ11qizevOEeCrs=
 github.com/smartcontractkit/chainlink-ccv/deployment v0.0.2-0.20260428205321-9ce8f4c44d23/go.mod h1:V+wrhuNve+JiFwoBr25d6y0lL1rYSCSJhTFyloL3ueo=
-github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e h1:uTuCrOqBZeYfIl2QG70KuCG7xpubUETFJpHiip5+7FU=
-github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e/go.mod h1:GlEVw7ziizXoMfzl1onNSwansrVBLHhj5gUJlGQpb4I=
+github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b h1:UMQ+MwHI341h+yARqeKmY/cagkB/dH0J34aMoJG00io=
+github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b/go.mod h1:GlEVw7ziizXoMfzl1onNSwansrVBLHhj5gUJlGQpb4I=
 github.com/smartcontractkit/chainlink-common/keystore v1.2.0 h1:1BH/b14CkGjArfzznlioQpIJiynECWVT48JUP9E277U=
 github.com/smartcontractkit/chainlink-common/keystore v1.2.0/go.mod h1:9R/74vN+bJ5PbkOyM/pUy/AeAZaRwYb/k4XPeXcbDio=
 github.com/smartcontractkit/chainlink-common/pkg/chipingress v0.0.11-0.20260601211238-9f526774fef0 h1:NExKM/D0HneOq/N5LGTbkV4VOa0UHCvfTNEb4GqYpto=
```

### integration-tests/load/go.mod
```diff
@@ -20,7 +20,7 @@ require (
 	github.com/smartcontractkit/chainlink-ccip/chains/evm v0.0.0-20260506144252-c100eabfda74
 	github.com/smartcontractkit/chainlink-ccip/chains/solana v0.0.0-20260506144252-c100eabfda74
 	github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20260511195239-0f6e1b177fc7
-	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e
+	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b
 	github.com/smartcontractkit/chainlink-deployments-framework v0.105.0
 	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260609161557-8ceae53b8ab1
 	github.com/smartcontractkit/chainlink-testing-framework/framework v0.16.1
```

### integration-tests/load/go.sum
```diff
@@ -1633,8 +1633,8 @@ github.com/smartcontractkit/chainlink-ccv v0.0.2-0.20260428133800-3b1484e8b1fd h
 github.com/smartcontractkit/chainlink-ccv v0.0.2-0.20260428133800-3b1484e8b1fd/go.mod h1:SBN8Urnh5sQvrQRbSo1Nr8coWatHg8LZoPw3R/42sho=
 github.com/smartcontractkit/chainlink-ccv/deployment v0.0.2-0.20260428205321-9ce8f4c44d23 h1:1Rt4HLpwbRN1YtBFcbsxSJYIiUP2wJ11qizevOEeCrs=
 github.com/smartcontractkit/chainlink-ccv/deployment v0.0.2-0.20260428205321-9ce8f4c44d23/go.mod h1:V+wrhuNve+JiFwoBr25d6y0lL1rYSCSJhTFyloL3ueo=
-github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e h1:uTuCrOqBZeYfIl2QG70KuCG7xpubUETFJpHiip5+7FU=
-github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e/go.mod h1:GlEVw7ziizXoMfzl1onNSwansrVBLHhj5gUJlGQpb4I=
+github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b h1:UMQ+MwHI341h+yARqeKmY/cagkB/dH0J34aMoJG00io=
+github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b/go.mod h1:GlEVw7ziizXoMfzl1onNSwansrVBLHhj5gUJlGQpb4I=
 github.com/smartcontractkit/chainlink-common/keystore v1.2.0 h1:1BH/b14CkGjArfzznlioQpIJiynECWVT48JUP9E277U=
 github.com/smartcontractkit/chainlink-common/keystore v1.2.0/go.mod h1:9R/74vN+bJ5PbkOyM/pUy/AeAZaRwYb/k4XPeXcbDio=
 github.com/smartcontractkit/chainlink-common/pkg/chipingress v0.0.11-0.20260601211238-9f526774fef0 h1:NExKM/D0HneOq/N5LGTbkV4VOa0UHCvfTNEb4GqYpto=
```

### system-tests/lib/go.mod
```diff
@@ -33,7 +33,7 @@ require (
 	github.com/smartcontractkit/chain-selectors v1.0.101
 	github.com/smartcontractkit/chainlink-aptos v0.0.0-20260609211101-71d38bd6a0a9
 	github.com/smartcontractkit/chainlink-ccip/chains/solana v0.0.0-20260415165642-49f23e4d76cc
-	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e
+	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b
 	github.com/smartcontractkit/chainlink-common/keystore v1.2.0
 	github.com/smartcontractkit/chainlink-deployments-framework v0.105.0
 	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260609161557-8ceae53b8ab1
```

### system-tests/lib/go.sum
```diff
@@ -1540,8 +1540,8 @@ github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20260
 github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20260511195239-0f6e1b177fc7/go.mod h1:67YbnoglYD61Pz/jTVCgav9wFq7S35OU8UyQSvPllRw=
 github.com/smartcontractkit/chainlink-ccv v0.0.2-0.20260428133800-3b1484e8b1fd h1:IMopuENFVS63AerRELdfWo6o60UNUidcldJOxJLmk24=
 github.com/smartcontractkit/chainlink-ccv v0.0.2-0.20260428133800-3b1484e8b1fd/go.mod h1:SBN8Urnh5sQvrQRbSo1Nr8coWatHg8LZoPw3R/42sho=
-github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e h1:uTuCrOqBZeYfIl2QG70KuCG7xpubUETFJpHiip5+7FU=
-github.com/smartcontractkit/chainlink-common v0.11.2-0.20260609183712-678afb1edd2e/go.mod h1:GlEVw7ziizXoMfzl1onNSwansrVBLHhj5gUJlGQpb4I=
+github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b h1:UMQ+MwHI341h+yARqeKmY/cagkB/dH0J34aMoJG00io=
+github.com/smartcontractkit/chainlink-common v0.11.2-0.20260610184803-96d1e031407b/go.mod h1:GlEVw7ziizXoMfzl1onNSwansrVBLHhj5gUJlGQpb4I=
 github.com/smartcontractkit/chainlink-common/keystore v1.2.0 h1:1BH/b14CkGjArfzznlioQpIJiynECWVT48JUP9E277U=
 github.com/smartcontractkit/chainlink-common/keystore v1.2.0/go.mod h1:9R/74vN+bJ5PbkOyM/pUy/AeAZaRwYb/k4XPeXcbDio=
 github.com/smartcontractkit/chainlink-common/pkg/chipingress v0.0.11-0.20260601211238-9f526774fef0 h1:NExKM/D0HneOq/N5LGTbkV4VOa0UHCvfTNEb4GqYpto=
```
