# [?] chore&fix: panic/error handling while enumerating pins

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2022-04-15
Source: https://github.com/ipfs/kubo/commit/ae15fcd195e80d6e1bf3c8f902d3a9eba1e6270a
Type: security-commit

## Details
chore&fix: panic/error handling while enumerating pins

switch to version from https://github.com/ipfs/go-pinning-service-http-client/pull/18
to see if CI E2E tests pass

## Patch
### go.mod
```diff
@@ -53,7 +53,7 @@ require (
 	github.com/ipfs/go-mfs v0.2.1
 	github.com/ipfs/go-namesys v0.4.0
 	github.com/ipfs/go-path v0.2.2
-	github.com/ipfs/go-pinning-service-http-client v0.1.0
+	github.com/ipfs/go-pinning-service-http-client v0.1.1
 	github.com/ipfs/go-unixfs v0.3.1
 	github.com/ipfs/go-unixfsnode v1.1.3
 	github.com/ipfs/go-verifcid v0.0.1
```

### go.sum
```diff
@@ -614,8 +614,8 @@ github.com/ipfs/go-peertaskqueue v0.1.1/go.mod h1:Jmk3IyCcfl1W3jTW3YpghSwSEC6IJ3
 github.com/ipfs/go-peertaskqueue v0.2.0/go.mod h1:5/eNrBEbtSKWCG+kQK8K8fGNixoYUnr+P7jivavs9lY=
 github.com/ipfs/go-peertaskqueue v0.7.0 h1:VyO6G4sbzX80K58N60cCaHsSsypbUNs1GjO5seGNsQ0=
 github.com/ipfs/go-peertaskqueue v0.7.0/go.mod h1:M/akTIE/z1jGNXMU7kFB4TeSEFvj68ow0Rrb04donIU=
-github.com/ipfs/go-pinning-service-http-client v0.1.0 h1:Au0P4NglL5JfzhNSZHlZ1qra+IcJyO3RWMd9EYCwqSY=
-github.com/ipfs/go-pinning-service-http-client v0.1.0/go.mod h1:tcCKmlkWWH9JUUkKs8CrOZBanacNc1dmKLfjlyXAMu4=
+github.com/ipfs/go-pinning-service-http-client v0.1.1 h1:Bar+Vi60A0zI8GSSrumVqnbFg6qkUgZSQTX9sV5jWrA=
+github.com/ipfs/go-pinning-service-http-client v0.1.1/go.mod h1:i6tC2nWOnJbZZUQPgxOlrg4CX8bhQZMh4II09FxvD58=
 github.com/ipfs/go-unixfs v0.2.4/go.mod h1:SUdisfUjNoSDzzhGVxvCL9QO/nKdwXdr+gbMUdqcbYw=
 github.com/ipfs/go-unixfs v0.3.1 h1:LrfED0OGfG98ZEegO4/xiprx2O+yS+krCMQSp7zLVv8=
 github.com/ipfs/go-unixfs v0.3.1/go.mod h1:h4qfQYzghiIc8ZNFKiLMFWOTzrWIAtzYQ59W/pCFf1o=
```
