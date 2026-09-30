# [?] fix: bump ibc to address security advisory (#513)

## Summary
Severity: Unknown
Chain: Noble
Component: noble-assets/noble
Published: 2025-03-12
Source: https://github.com/noble-assets/noble/commit/ea16e65b132b8758d69095446aa87a3edaf764e2
Type: security-commit

## Details
fix: bump ibc to address security advisory (#513)

## Patch
### .changelog/v9.0.2/dependencies/513-bump-ibc.md
```diff
@@ -0,0 +1 @@
+- Bump IBC to [`v8.7.0`](https://github.com/cosmos/ibc-go/releases/tag/v8.7.0) to resolve [ISA-2025-001](https://github.com/cosmos/ibc-go/security/advisories/GHSA-4wf3-5qj9-368v) security advisory. ([#513](https://github.com/noble-assets/noble/pull/513))
```

### .changelog/v9.0.2/summary.md
```diff
@@ -0,0 +1,3 @@
+*Mar 12, 2025*
+
+This is a non-consensus breaking patch to the v9 Argentum release line.
```

### CHANGELOG.md
```diff
@@ -1,5 +1,15 @@
 # CHANGELOG
 
+## v9.0.2
+
+*Mar 12, 2025*
+
+This is a non-consensus breaking patch to the v9 Argentum release line.
+
+### DEPENDENCIES
+
+- Bump IBC to [`v8.7.0`](https://github.com/cosmos/ibc-go/releases/tag/v8.7.0) to resolve [ISA-2025-001](https://github.com/cosmos/ibc-go/security/advisories/GHSA-4wf3-5qj9-368v) security advisory. ([#513](https://github.com/noble-assets/noble/pull/513))
+
 ## v9.0.1
 
 *Mar 4, 2025*
```

### e2e/go.mod
```diff
@@ -10,7 +10,7 @@ require (
 	github.com/circlefin/noble-fiattokenfactory v0.0.0-20250123235012-5f9bd9dd2c5b
 	github.com/cosmos/cosmos-sdk v0.50.12
 	github.com/cosmos/gogoproto v1.7.0
-	github.com/cosmos/ibc-go/v8 v8.6.1
+	github.com/cosmos/ibc-go/v8 v8.7.0
 	github.com/docker/docker v24.0.9+incompatible
 	github.com/ethereum/go-ethereum v1.14.13
 	github.com/monerium/module-noble/v2 v2.0.0
```

### e2e/go.sum
```diff
@@ -396,8 +396,8 @@ github.com/cosmos/iavl v1.2.2 h1:qHhKW3I70w+04g5KdsdVSHRbFLgt3yY3qTMd4Xa4rC8=
 github.com/cosmos/iavl v1.2.2/go.mod h1:GiM43q0pB+uG53mLxLDzimxM9l/5N9UuSY3/D0huuVw=
 github.com/cosmos/ibc-go/modules/capability v1.0.1 h1:ibwhrpJ3SftEEZRxCRkH0fQZ9svjthrX2+oXdZvzgGI=
 github.com/cosmos/ibc-go/modules/capability v1.0.1/go.mod h1:rquyOV262nGJplkumH+/LeYs04P3eV8oB7ZM4Ygqk4E=
-github.com/cosmos/ibc-go/v8 v8.6.1 h1:35JQ9HttSDNLjy4J/ZxmmFbzw0cRVjoCRKkc3ngDZms=
-github.com/cosmos/ibc-go/v8 v8.6.1/go.mod h1:Hd3kDFNOhQ/EnYt8qb84/r78tA/lOYC3IkLMbpurs3I=
+github.com/cosmos/ibc-go/v8 v8.7.0 h1:HqhVOkO8bDpClXE81DFQgFjroQcTvtpm0tCS7SQVKVY=
+github.com/cosmos/ibc-go/v8 v8.7.0/go.mod h1:G2z+Q6ZQSMcyHI2+BVcJdvfOupb09M2h/tgpXOEdY6k=
 github.com/cosmos/ics23/go v0.11.0 h1:jk5skjT0TqX5e5QJbEnwXIS2yI2vnmLOgpQPeM5RtnU=
 github.com/cosmos/ics23/go v0.11.0/go.mod h1:A8OjxPE67hHST4Icw94hOxxFEJMBG031xIGF/JHNIY0=
 github.com/cosmos/interchain-security/v5 v5.1.1 h1:xmRRMeE4xoc+JAZUh0XzXFYWaGBtzFFj5SETuOgnEnY=
```

### go.mod
```diff
@@ -24,7 +24,7 @@ require (
 	github.com/cosmos/cosmos-sdk v0.50.12
 	github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v8 v8.2.0
 	github.com/cosmos/ibc-go/modules/capability v1.0.1
-	github.com/cosmos/ibc-go/v8 v8.6.1
+	github.com/cosmos/ibc-go/v8 v8.7.0
 	github.com/ethereum/go-ethereum v1.14.13
 	github.com/golangci/golangci-lint v1.61.0
 	github.com/gorilla/mux v1.8.1
```

### go.sum
```diff
@@ -465,8 +465,8 @@ github.com/cosmos/iavl v1.2.2 h1:qHhKW3I70w+04g5KdsdVSHRbFLgt3yY3qTMd4Xa4rC8=
 github.com/cosmos/iavl v1.2.2/go.mod h1:GiM43q0pB+uG53mLxLDzimxM9l/5N9UuSY3/D0huuVw=
 github.com/cosmos/ibc-go/modules/capability v1.0.1 h1:ibwhrpJ3SftEEZRxCRkH0fQZ9svjthrX2+oXdZvzgGI=
 github.com/cosmos/ibc-go/modules/capability v1.0.1/go.mod h1:rquyOV262nGJplkumH+/LeYs04P3eV8oB7ZM4Ygqk4E=
-github.com/cosmos/ibc-go/v8 v8.6.1 h1:35JQ9HttSDNLjy4J/ZxmmFbzw0cRVjoCRKkc3ngDZms=
-github.com/cosmos/ibc-go/v8 v8.6.1/go.mod h1:Hd3kDFNOhQ/EnYt8qb84/r78tA/lOYC3IkLMbpurs3I=
+github.com/cosmos/ibc-go/v8 v8.7.0 h1:HqhVOkO8bDpClXE81DFQgFjroQcTvtpm0tCS7SQVKVY=
+github.com/cosmos/ibc-go/v8 v8.7.0/go.mod h1:G2z+Q6ZQSMcyHI2+BVcJdvfOupb09M2h/tgpXOEdY6k=
 github.com/cosmos/ics23/go v0.11.0 h1:jk5skjT0TqX5e5QJbEnwXIS2yI2vnmLOgpQPeM5RtnU=
 github.com/cosmos/ics23/go v0.11.0/go.mod h1:A8OjxPE67hHST4Icw94hOxxFEJMBG031xIGF/JHNIY0=
 github.com/cosmos/ledger-cosmos-go v0.14.0 h1:WfCHricT3rPbkPSVKRH+L4fQGKYHuGOK9Edpel8TYpE=
```
