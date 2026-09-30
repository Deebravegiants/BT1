# [?] updated go.mod and go.sum to the latest version of github.com/koron/go-ssdp library that has the race condition fixed

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2019-11-21
Source: https://github.com/libp2p/go-libp2p/commit/93d0ace99efa5d8be6a0ddf83f601d304ddb0ee7
Type: security-commit

## Details
updated go.mod and go.sum to the latest version of github.com/koron/go-ssdp library that has the race condition fixed

## Patch
### go.mod
```diff
@@ -4,5 +4,7 @@ require (
 	github.com/huin/goupnp v1.0.0
 	github.com/jackpal/gateway v1.0.5
 	github.com/jackpal/go-nat-pmp v1.0.1
-	github.com/koron/go-ssdp v0.0.0-20180514024734-4a0ed625a78b
+	github.com/koron/go-ssdp v0.0.0-20191105050749-2e1c40ed0b5d
 )
+
+go 1.12
```

### go.sum
```diff
@@ -5,8 +5,8 @@ github.com/jackpal/gateway v1.0.5 h1:qzXWUJfuMdlLMtt0a3Dgt+xkWQiA5itDEITVJtuSwMc
 github.com/jackpal/gateway v1.0.5/go.mod h1:lTpwd4ACLXmpyiCTRtfiNyVnUmqT9RivzCDQetPfnjA=
 github.com/jackpal/go-nat-pmp v1.0.1 h1:i0LektDkO1QlrTm/cSuP+PyBCDnYvjPLGl4LdWEMiaA=
 github.com/jackpal/go-nat-pmp v1.0.1/go.mod h1:QPH045xvCAeXUZOxsnwmrtiCoxIr9eob+4orBN1SBKc=
-github.com/koron/go-ssdp v0.0.0-20180514024734-4a0ed625a78b h1:wxtKgYHEncAU00muMD06dzLiahtGM1eouRNOzVV7tdQ=
-github.com/koron/go-ssdp v0.0.0-20180514024734-4a0ed625a78b/go.mod h1:5Ky9EC2xfoUKUor0Hjgi2BJhCSXJfMOFlmyYrVKGQMk=
+github.com/koron/go-ssdp v0.0.0-20191105050749-2e1c40ed0b5d h1:68u9r4wEvL3gYg2jvAOgROwZ3H+Y3hIDk4tbbmIjcYQ=
+github.com/koron/go-ssdp v0.0.0-20191105050749-2e1c40ed0b5d/go.mod h1:5Ky9EC2xfoUKUor0Hjgi2BJhCSXJfMOFlmyYrVKGQMk=
 golang.org/x/net v0.0.0-20181011144130-49bb7cea24b1 h1:Y/KGZSOdz/2r0WJ9Mkmz6NJBusp0kiNx1Cn82lzJQ6w=
 golang.org/x/net v0.0.0-20181011144130-49bb7cea24b1/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/text v0.3.0 h1:g61tztE5qeGQ89tm6NTjjM9VPIm088od1l6aSorWRWg=
```
