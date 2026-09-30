# [?] ci: fix nancy vulnerabilities issue;

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2024-03-08
Source: https://github.com/bnb-chain/bsc/commit/0dc4b1f119d61561bd6032b9cb3a8d70cf1bbb4f
Type: security-commit

## Details
ci: fix nancy vulnerabilities issue;

## Patch
### go.mod
```diff
@@ -34,7 +34,7 @@ require (
 	github.com/gballet/go-verkle v0.1.1-0.20231031103413-a67434b50f46
 	github.com/gofrs/flock v0.8.1
 	github.com/golang-jwt/jwt/v4 v4.5.0
-	github.com/golang/protobuf v1.5.3
+	github.com/golang/protobuf v1.5.4
 	github.com/golang/snappy v0.0.5-0.20220116011046-fa5810519dcb
 	github.com/google/gofuzz v1.2.0
 	github.com/google/pprof v0.0.0-20231023181126-ff6d637d2a7b
@@ -281,7 +281,7 @@ require (
 	google.golang.org/appengine v1.6.7 // indirect
 	google.golang.org/genproto v0.0.0-20230410155749-daa745c078e1 // indirect
 	google.golang.org/grpc v1.56.3 // indirect
-	google.golang.org/protobuf v1.30.0 // indirect
+	google.golang.org/protobuf v1.33.0 // indirect
 	gopkg.in/inf.v0 v0.9.1 // indirect
 	gopkg.in/yaml.v2 v2.4.0 // indirect
 	k8s.io/apimachinery v0.20.0 // indirect
```

### go.sum
```diff
@@ -606,8 +606,8 @@ github.com/golang/protobuf v1.4.3/go.mod h1:oDoupMAO8OvCJWAcko0GGGIgR6R6ocIYbsSw
 github.com/golang/protobuf v1.5.0/go.mod h1:FsONVRAS9T7sI+LIUmWTfcYkHO4aIWwzhcaSAoJOfIk=
 github.com/golang/protobuf v1.5.1/go.mod h1:DopwsBzvsk0Fs44TXzsVbJyPhcCPeIwnvohx4u74HPM=
 github.com/golang/protobuf v1.5.2/go.mod h1:XVQd3VNwM+JqD3oG2Ue2ip4fOMUkwXdXDdiuN0vRsmY=
-github.com/golang/protobuf v1.5.3 h1:KhyjKVUg7Usr/dYsdSqoFveMYd5ko72D+zANwlG1mmg=
-github.com/golang/protobuf v1.5.3/go.mod h1:XVQd3VNwM+JqD3oG2Ue2ip4fOMUkwXdXDdiuN0vRsmY=
+github.com/golang/protobuf v1.5.4 h1:i7eJL8qZTpSEXOPTxNKhASYpMn+8e5Q6AdndVa1dWek=
+github.com/golang/protobuf v1.5.4/go.mod h1:lnTiLA8Wa4RWRcIUkrtSVa5nRhsEGBg48fD6rSs7xps=
 github.com/golang/snappy v0.0.0-20170215233205-553a64147049/go.mod h1:/XxbfmMg8lxefKM7IXC3fBNl/7bRcc72aCRzEWrmP2Q=
 github.com/golang/snappy v0.0.0-20180518054509-2e65f85255db/go.mod h1:/XxbfmMg8lxefKM7IXC3fBNl/7bRcc72aCRzEWrmP2Q=
 github.com/golang/snappy v0.0.1/go.mod h1:/XxbfmMg8lxefKM7IXC3fBNl/7bRcc72aCRzEWrmP2Q=
@@ -2345,8 +2345,8 @@ google.golang.org/protobuf v1.25.1-0.20201208041424-160c7477e0e8/go.mod h1:hFxJC
 google.golang.org/protobuf v1.26.0-rc.1/go.mod h1:jlhhOSvTdKEhbULTjvd4ARK9grFBp09yW+WbY/TyQbw=
 google.golang.org/protobuf v1.26.0/go.mod h1:9q0QmTI4eRPtz6boOQmLYwt+qCgq0jsYwAQnmE0givc=
 google.golang.org/protobuf v1.27.1/go.mod h1:9q0QmTI4eRPtz6boOQmLYwt+qCgq0jsYwAQnmE0givc=
-google.golang.org/protobuf v1.30.0 h1:kPPoIgf3TsEvrm0PFe15JQ+570QVxYzEvvHqChK+cng=
-google.golang.org/protobuf v1.30.0/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
+google.golang.org/protobuf v1.33.0 h1:uNO2rsAINq/JlFpSdYEKIZ0uKD/R9cpdv0T+yoGwGmI=
+google.golang.org/protobuf v1.33.0/go.mod h1:c6P6GXX6sHbq/GpV6MGZEdwhWPcYBgnhAHhKbcUYpos=
 gopkg.in/alecthomas/kingpin.v2 v2.2.6/go.mod h1:FMv+mEhP44yOT+4EoQTLFTRgOQ1FBLkstjWtayDeSgw=
 gopkg.in/bsm/ratelimit.v1 v1.0.0-20160220154919-db14e161995a/go.mod h1:KF9sEfUPAXdG8Oev9e99iLGnl2uJMjc5B+4y3O7x610=
 gopkg.in/cenkalti/backoff.v1 v1.1.0/go.mod h1:J6Vskwqd+OMVJl8C33mmtxTBs2gyzfv7UDAkHu8BrjI=
```
