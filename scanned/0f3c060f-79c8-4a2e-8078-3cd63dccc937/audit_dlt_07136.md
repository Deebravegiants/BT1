# [?] Update sys lib to prevent arm64 crash (#1046)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-05-22
Source: https://github.com/celo-org/celo-blockchain/commit/2e536280bcaa2a47b2156077b0bad78227787abf
Type: security-commit

## Details
Update sys lib to prevent arm64 crash (#1046)

### Description

This issue https://github.com/golang/go/issues/36622 started causing crashes for us. Tested the fix with a new android build and it does not crash any more

## Patch
### go.mod
```diff
@@ -66,7 +66,7 @@ require (
 	golang.org/x/mobile v0.0.0-20200329125638-4c31acba0007 // indirect
 	golang.org/x/net v0.0.0-20190628185345-da137c7871d7 // indirect
 	golang.org/x/sync v0.0.0-20190423024810-112230192c58
-	golang.org/x/sys v0.0.0-20191210023423-ac6580df4449
+	golang.org/x/sys v0.0.0-20200519105757-fe76b779f299
 	golang.org/x/text v0.3.2
 	gopkg.in/natefinch/npipe.v2 v2.0.0-20160621034901-c1b8fa8bdcce
 	gopkg.in/olebedev/go-duktape.v3 v3.0.0-20190213234257-ec84240a7772
```

### go.sum
```diff
@@ -255,6 +255,8 @@ golang.org/x/sys v0.0.0-20190712062909-fae7ac547cb7/go.mod h1:h1NjWce9XRLGQEsW7w
 golang.org/x/sys v0.0.0-20191026070338-33540a1f6037/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20191210023423-ac6580df4449 h1:gSbV7h1NRL2G1xTg/owz62CST1oJBmxy4QpMMregXVQ=
 golang.org/x/sys v0.0.0-20191210023423-ac6580df4449/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
+golang.org/x/sys v0.0.0-20200519105757-fe76b779f299 h1:DYfZAGf2WMFjMxbgTjaC+2HC7NkNAQs+6Q8b9WEB/F4=
+golang.org/x/sys v0.0.0-20200519105757-fe76b779f299/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.2 h1:tW2bmiBqwgJj/UpqtC8EpXEZVYOwU0yG4iWbprSVAcs=
 golang.org/x/text v0.3.2/go.mod h1:bEr9sfX3Q8Zfm5fL9x+3itogRgK3+ptLWKqgva+5dAk=
```
