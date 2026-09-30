# [?] Upgrade lachesis-base to fix race condition (#80)

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2023-12-18
Source: https://github.com/0xsoniclabs/sonic/commit/caea3b445d40a37fc50a537342b0545ec20a3d3e
Type: security-commit

## Details
Upgrade lachesis-base to fix race condition (#80)

## Patch
### go.mod
```diff
@@ -3,7 +3,7 @@ module github.com/Fantom-foundation/go-opera
 go 1.21
 
 require (
-	github.com/Fantom-foundation/lachesis-base v0.0.0-20230629034932-42bae8eeb426
+	github.com/Fantom-foundation/lachesis-base v0.0.0-20231215134255-2653b301ce62
 	github.com/allegro/bigcache v1.2.1 // indirect
 	github.com/certifi/gocertifi v0.0.0-20191021191039-0944d244cd40 // indirect
 	github.com/cespare/cp v1.1.1
```

### go.sum
```diff
@@ -63,8 +63,8 @@ github.com/Fantom-foundation/Tosca v0.0.0-20231211120117-160cf8af1fde h1:YxmvjNn
 github.com/Fantom-foundation/Tosca v0.0.0-20231211120117-160cf8af1fde/go.mod h1:XfSNrGyRoCCpph5NeHriyuEh8wZw90w4mNH42vbFJ/g=
 github.com/Fantom-foundation/go-ethereum-substate v1.1.1-0.20231003122306-febfe681b4a7 h1:AWVp8bMwysTNE2/yORyxk4KF+isK9wFkPeLsT7SYS10=
 github.com/Fantom-foundation/go-ethereum-substate v1.1.1-0.20231003122306-febfe681b4a7/go.mod h1:qk1JSsat4pdiDpbt6T4MmcGp02kiq8xOREvDhiKJoFQ=
-github.com/Fantom-foundation/lachesis-base v0.0.0-20230629034932-42bae8eeb426 h1:TCsCxpzd2ETqHJMdkw09Ck1mmnNgx/Z4h6i6kDOexYI=
-github.com/Fantom-foundation/lachesis-base v0.0.0-20230629034932-42bae8eeb426/go.mod h1:Ogv5etzSmM2rQ4eN3OfmyitwWaaPjd4EIDiW/NAbYGk=
+github.com/Fantom-foundation/lachesis-base v0.0.0-20231215134255-2653b301ce62 h1:mYxGUl4Vgv7Gh7gxH5I9bchalFMBzExf94w8ISTEOaY=
+github.com/Fantom-foundation/lachesis-base v0.0.0-20231215134255-2653b301ce62/go.mod h1:Ogv5etzSmM2rQ4eN3OfmyitwWaaPjd4EIDiW/NAbYGk=
 github.com/Joker/hpp v1.0.0/go.mod h1:8x5n+M1Hp5hC0g8okX3sR3vFQwynaX/UgSOM9MeBKzY=
 github.com/Joker/jade v1.0.1-0.20190614124447-d475f43051e7/go.mod h1:6E6s8o2AE4KhCrqr6GRJjdC/gNfTdxkIXvuGZZda2VM=
 github.com/OneOfOne/xxhash v1.2.2/go.mod h1:HSdplMjZKSmBqAxg5vPj2TmRDmfkzw+cTzAElWljhcU=
```
