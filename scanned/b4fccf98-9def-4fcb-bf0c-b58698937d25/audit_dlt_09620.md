# [?] Problem: security patch from ibc-go is not included (#1766)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/cronos
Published: 2025-03-12
Source: https://github.com/crypto-org-chain/cronos/commit/197ac8b7c303065d44f729259847fd9f71186144
Type: security-commit

## Details
Problem: security patch from ibc-go is not included (#1766)

## Patch
### CHANGELOG.md
```diff
@@ -11,6 +11,7 @@
 * (versiondb) [#1751](https://github.com/crypto-org-chain/cronos/pull/1751) Add missing Destroy for read options to properly hold and release options reference.
 * (versiondb) [#1758](https://github.com/crypto-org-chain/cronos/pull/1758) Avoid ReadOptions mutated by reference release in iterator.
 * [#1759](https://github.com/crypto-org-chain/cronos/pull/1759) Fix version mismatch happen occasionally.
+* [#1766](https://github.com/crypto-org-chain/cronos/pull/1766) Include a security patch from ibc-go `v8.7.0`.
 
 ### Improvements
 
```

### go.mod
```diff
@@ -22,9 +22,9 @@ require (
 	github.com/cosmos/cosmos-proto v1.0.0-beta.5
 	github.com/cosmos/cosmos-sdk v0.50.9
 	github.com/cosmos/gogoproto v1.7.0
-	github.com/cosmos/ibc-go/modules/apps/callbacks v0.0.0-20240913130017-6b2554360c0e // v8.5.1
+	github.com/cosmos/ibc-go/modules/apps/callbacks v0.0.0-20250312150146-53eaba19375d // v8.7.0
 	github.com/cosmos/ibc-go/modules/capability v1.0.1
-	github.com/cosmos/ibc-go/v8 v8.6.1
+	github.com/cosmos/ibc-go/v8 v8.7.0
 	github.com/cosmos/rosetta v0.50.3-1
 	github.com/crypto-org-chain/cronos/store v0.0.4
 	github.com/crypto-org-chain/cronos/versiondb v0.0.0-00010101000000-000000000000
```

### go.sum
```diff
@@ -395,12 +395,12 @@ github.com/cosmos/gogoproto v1.7.0 h1:79USr0oyXAbxg3rspGh/m4SWNyoz/GLaAh0QlCe2fr
 github.com/cosmos/gogoproto v1.7.0/go.mod h1:yWChEv5IUEYURQasfyBW5ffkMHR/90hiHgbNgrtp4j0=
 github.com/cosmos/iavl v1.2.4-0.20241218014611-3b0ad9922f9f h1:ex8R1/5/ghhCBEwSWr2L2+OSnWU0A6Pe68cROdGiVX4=
 github.com/cosmos/iavl v1.2.4-0.20241218014611-3b0ad9922f9f/go.mod h1:GiM43q0pB+uG53mLxLDzimxM9l/5N9UuSY3/D0huuVw=
-github.com/cosmos/ibc-go/modules/apps/callbacks v0.0.0-20240913130017-6b2554360c0e h1:jMqihcJRBdpRrKGOMS1bDyyoo2JoQxv4QmMCwK3HSvI=
-github.com/cosmos/ibc-go/modules/apps/callbacks v0.0.0-20240913130017-6b2554360c0e/go.mod h1:akR14gsU5YD5S1G5I6lOI7z51OjR1vJko06Rs/3/Ym0=
+github.com/cosmos/ibc-go/modules/apps/callbacks v0.0.0-20250312150146-53eaba19375d h1:QOEFyekL1u4FvZTLTQDvrnUYfhaiwhVs79acM2B8Zfk=
+github.com/cosmos/ibc-go/modules/apps/callbacks v0.0.0-20250312150146-53eaba19375d/go.mod h1:akR14gsU5YD5S1G5I6lOI7z51OjR1vJko06Rs/3/Ym0=
 github.com/cosmos/ibc-go/modules/capability v1.0.1 h1:ibwhrpJ3SftEEZRxCRkH0fQZ9svjthrX2+oXdZvzgGI=
 github.com/cosmos/ibc-go/modules/capability v1.0.1/go.mod h1:rquyOV262nGJplkumH+/LeYs04P3eV8oB7ZM4Ygqk4E=
-github.com/cosmos/ibc-go/v8 v8.6.1 h1:35JQ9HttSDNLjy4J/ZxmmFbzw0cRVjoCRKkc3ngDZms=
-github.com/cosmos/ibc-go/v8 v8.6.1/go.mod h1:Hd3kDFNOhQ/EnYt8qb84/r78tA/lOYC3IkLMbpurs3I=
+github.com/cosmos/ibc-go/v8 v8.7.0 h1:HqhVOkO8bDpClXE81DFQgFjroQcTvtpm0tCS7SQVKVY=
+github.com/cosmos/ibc-go/v8 v8.7.0/go.mod h1:G2z+Q6ZQSMcyHI2+BVcJdvfOupb09M2h/tgpXOEdY6k=
 github.com/cosmos/ics23/go v0.11.0 h1:jk5skjT0TqX5e5QJbEnwXIS2yI2vnmLOgpQPeM5RtnU=
 github.com/cosmos/ics23/go v0.11.0/go.mod h1:A8OjxPE67hHST4Icw94hOxxFEJMBG031xIGF/JHNIY0=
 github.com/cosmos/keyring v1.2.0 h1:8C1lBP9xhImmIabyXW4c3vFjjLiBdGCmfLUfeZlV1Yo=
```

### gomod2nix.toml
```diff
@@ -190,14 +190,14 @@ schema = 3
     version = "v1.2.4-0.20241218014611-3b0ad9922f9f"
     hash = "sha256-WbNyKZmKBr2R1YaVfGVdSH9dX6AqFynOwd2dmpTX3ZI="
   [mod."github.com/cosmos/ibc-go/modules/apps/callbacks"]
-    version = "v0.0.0-20240913130017-6b2554360c0e"
+    version = "v0.0.0-20250312150146-53eaba19375d"
     hash = "sha256-mL+g8WB+fLUlTKMnrdn8rTgw2gqXsHlky3/BTsyfek0="
   [mod."github.com/cosmos/ibc-go/modules/capability"]
     version = "v1.0.1"
     hash = "sha256-iRhj2WTr99DgAl80h25pxtkO6iHYjyHflwpxKKG5b6E="
   [mod."github.com/cosmos/ibc-go/v8"]
-    version = "v8.6.1"
-    hash = "sha256-1xeBTIN68uoRCyohelTfnMql2ijRxktUoZ9ra/0mMQk="
+    version = "v8.7.0"
+    hash = "sha256-axMi6WoRyrtIGpZ24XQ1N0e2gUQ4ZbqnPVpYsqwmUmU="
   [mod."github.com/cosmos/ics23/go"]
     version = "v0.11.0"
     hash = "sha256-mgU/pqp4kASmW/bP0z6PzssfjRp7GU9ioyvNlDdGC+E="
```
