# [?] Problem: fix of deadlock when close tree is not included (#1725)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/cronos
Published: 2024-12-18
Source: https://github.com/crypto-org-chain/cronos/commit/d03b8d82fef43f2ed9fe00c10df8775e93352aae
Type: security-commit

## Details
Problem: fix of deadlock when close tree is not included (#1725)

## Patch
### CHANGELOG.md
```diff
@@ -5,6 +5,7 @@
 ### Bug Fixes
 
 * [#1720](https://github.com/crypto-org-chain/cronos/pull/1720) Include the fix of performance regression after upgrade in iavl.
+* [#1725](https://github.com/crypto-org-chain/cronos/pull/1725) Include the fix of deadlock when close tree in iavl.
 
 ### State Machine Breaking
 
```

### go.mod
```diff
@@ -89,7 +89,7 @@ require (
 	github.com/cosmos/btcutil v1.0.5 // indirect
 	github.com/cosmos/go-bip39 v1.0.0 // indirect
 	github.com/cosmos/gogogateway v1.2.0 // indirect
-	github.com/cosmos/iavl v1.2.3 // indirect
+	github.com/cosmos/iavl v1.2.4-0.20241218014611-3b0ad9922f9f // indirect
 	github.com/cosmos/ics23/go v0.11.0 // indirect
 	github.com/cosmos/ledger-cosmos-go v0.13.3 // indirect
 	github.com/cosmos/rosetta-sdk-go v0.10.0 // indirect
```

### go.sum
```diff
@@ -393,6 +393,8 @@ github.com/cosmos/gogoproto v1.7.0 h1:79USr0oyXAbxg3rspGh/m4SWNyoz/GLaAh0QlCe2fr
 github.com/cosmos/gogoproto v1.7.0/go.mod h1:yWChEv5IUEYURQasfyBW5ffkMHR/90hiHgbNgrtp4j0=
 github.com/cosmos/iavl v1.2.3 h1:XkESLkGuNikscRsIOSlYMsBaE+Ae7QvXt6e2zOoCgwA=
 github.com/cosmos/iavl v1.2.3/go.mod h1:GiM43q0pB+uG53mLxLDzimxM9l/5N9UuSY3/D0huuVw=
+github.com/cosmos/iavl v1.2.4-0.20241218014611-3b0ad9922f9f h1:ex8R1/5/ghhCBEwSWr2L2+OSnWU0A6Pe68cROdGiVX4=
+github.com/cosmos/iavl v1.2.4-0.20241218014611-3b0ad9922f9f/go.mod h1:GiM43q0pB+uG53mLxLDzimxM9l/5N9UuSY3/D0huuVw=
 github.com/cosmos/ibc-go/modules/apps/callbacks v0.0.0-20240913130017-6b2554360c0e h1:jMqihcJRBdpRrKGOMS1bDyyoo2JoQxv4QmMCwK3HSvI=
 github.com/cosmos/ibc-go/modules/apps/callbacks v0.0.0-20240913130017-6b2554360c0e/go.mod h1:akR14gsU5YD5S1G5I6lOI7z51OjR1vJko06Rs/3/Ym0=
 github.com/cosmos/ibc-go/modules/capability v1.0.1 h1:ibwhrpJ3SftEEZRxCRkH0fQZ9svjthrX2+oXdZvzgGI=
```
