# [?] Remove MaxConnectionAge gRPC StreamID overflow mitigation (#1388)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2023-06-20
Source: https://github.com/ava-labs/avalanchego/commit/ac3f2b42df7265fff66d9894d8b693598d3e053f
Type: security-commit

## Details
Remove MaxConnectionAge gRPC StreamID overflow mitigation (#1388)

## Patch
### go.mod
```diff
@@ -58,8 +58,8 @@ require (
 	golang.org/x/term v0.7.0
 	golang.org/x/time v0.0.0-20220922220347-f3bd1da661af
 	gonum.org/v1/gonum v0.11.0
-	google.golang.org/genproto v0.0.0-20221027153422-115e99e71e1c
-	google.golang.org/grpc v1.50.1
+	google.golang.org/genproto v0.0.0-20230306155012-7f2fa6fef1f4
+	google.golang.org/grpc v1.55.0
 	google.golang.org/protobuf v1.30.0
 	gopkg.in/natefinch/lumberjack.v2 v2.0.0
 )
@@ -91,7 +91,7 @@ require (
 	github.com/go-sourcemap/sourcemap v2.1.3+incompatible // indirect
 	github.com/go-stack/stack v1.8.1 // indirect
 	github.com/gogo/protobuf v1.3.2 // indirect
-	github.com/golang/protobuf v1.5.2 // indirect
+	github.com/golang/protobuf v1.5.3 // indirect
 	github.com/golang/snappy v0.0.4 // indirect
 	github.com/google/go-cmp v0.5.9 // indirect
 	github.com/google/uuid v1.3.0 // indirect
@@ -138,9 +138,9 @@ require (
 	go.opentelemetry.io/proto/otlp v0.19.0 // indirect
 	go.uber.org/atomic v1.10.0 // indirect
 	go.uber.org/multierr v1.8.0 // indirect
-	golang.org/x/net v0.7.0 // indirect
+	golang.org/x/net v0.8.0 // indirect
 	golang.org/x/sys v0.8.0 // indirect
-	golang.org/x/text v0.7.0 // indirect
+	golang.org/x/text v0.8.0 // indirect
 	gopkg.in/ini.v1 v1.67.0 // indirect
 	gopkg.in/yaml.v2 v2.4.0 // indirect
 	gopkg.in/yaml.v3 v3.0.1 // indirect
```

### go.sum
```diff
@@ -222,8 +222,8 @@ github.com/golang-jwt/jwt v3.2.2+incompatible/go.mod h1:8pz2t5EyA70fFQQSrl6XZXzq
 github.com/golang-jwt/jwt/v4 v4.3.0 h1:kHL1vqdqWNfATmA0FNMdmZNMyZI1U6O31X4rlIPoBog=
 github.com/golang-jwt/jwt/v4 v4.3.0/go.mod h1:/xlHOz8bRuivTWchD4jCa+NbatV+wEUSzwAxVc6locg=
 github.com/golang/glog v0.0.0-20160126235308-23def4e6c14b/go.mod h1:SBH7ygxi8pfUlaOkMMuAQtPIUF8ecWP5IEl/CR7VP2Q=
-github.com/golang/glog v1.0.0 h1:nfP3RFugxnNRyKgeWd4oI1nYvXpxrx8ck8ZrcizshdQ=
 github.com/golang/glog v1.0.0/go.mod h1:EWib/APOK0SL3dFbYqvxE3UYd8E6s1ouQ7iEp/0LWV4=
+github.com/golang/glog v1.1.0 h1:/d3pCKDPWNnvIWe0vVUpNP32qc8U3PDVxySP/y360qE=
 github.com/golang/groupcache v0.0.0-20190702054246-869f871628b6/go.mod h1:cIg4eruTrX1D+g88fzRXU5OdNfaM+9IcxsU14FzY7Hc=
 github.com/golang/groupcache v0.0.0-20191227052852-215e87163ea7/go.mod h1:cIg4eruTrX1D+g88fzRXU5OdNfaM+9IcxsU14FzY7Hc=
 github.com/golang/groupcache v0.0.0-20200121045136-8c9f03a8e57e/go.mod h1:cIg4eruTrX1D+g88fzRXU5OdNfaM+9IcxsU14FzY7Hc=
@@ -251,8 +251,9 @@ github.com/golang/protobuf v1.4.1/go.mod h1:U8fpvMrcmy5pZrNK1lt4xCsGvpyWQ/VVv6QD
 github.com/golang/protobuf v1.4.2/go.mod h1:oDoupMAO8OvCJWAcko0GGGIgR6R6ocIYbsSw735rRwI=
 github.com/golang/protobuf v1.4.3/go.mod h1:oDoupMAO8OvCJWAcko0GGGIgR6R6ocIYbsSw735rRwI=
 github.com/golang/protobuf v1.5.0/go.mod h1:FsONVRAS9T7sI+LIUmWTfcYkHO4aIWwzhcaSAoJOfIk=
-github.com/golang/protobuf v1.5.2 h1:ROPKBNFfQgOUMifHyP+KYbvpjbdoFNs+aK7DXlji0Tw=
 github.com/golang/protobuf v1.5.2/go.mod h1:XVQd3VNwM+JqD3oG2Ue2ip4fOMUkwXdXDdiuN0vRsmY=
+github.com/golang/protobuf v1.5.3 h1:KhyjKVUg7Usr/dYsdSqoFveMYd5ko72D+zANwlG1mmg=
+github.com/golang/protobuf v1.5.3/go.mod h1:XVQd3VNwM+JqD3oG2Ue2ip4fOMUkwXdXDdiuN0vRsmY=
 github.com/golang/snappy v0.0.4 h1:yAGX7huGHXlcLOEtBnF4w7FQwA26wojNCwOYAEhLjQM=
 github.com/golang/snappy v0.0.4/go.mod h1:/XxbfmMg8lxefKM7IXC3fBNl/7bRcc72aCRzEWrmP2Q=
 github.com/gomodule/redigo v1.7.1-0.20190724094224-574c33c3df38/go.mod h1:B4C85qUVwatsJoIUNIfCRsp7qO0iAmpGFZ4EELWSbC4=
@@ -703,8 +704,8 @@ golang.org/x/net v0.0.0-20210428140749-89ef3d95e781/go.mod h1:OJAsFXCWl8Ukc7SiCT
 golang.org/x/net v0.0.0-20211008194852-3b03d305991f/go.mod h1:9nx3DQGgdP8bBQD5qxJ1jj9UTztislL4KSBs9R2vV5Y=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
 golang.org/x/net v0.0.0-20220607020251-c690dde0001d/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
-golang.org/x/net v0.7.0 h1:rJrUqqhjsgNp7KqAIc25s9pZnjU7TUcSY7HcVZjdn1g=
-golang.org/x/net v0.7.0/go.mod h1:2Tu9+aMcznHK/AK1HMvgo6xiTLG5rD5rZLDS+rp2Bjs=
+golang.org/x/net v0.8.0 h1:Zrh2ngAOFYneWTAIAPethzeaQLuHwhuBkuV6ZiRnUaQ=
+golang.org/x/net v0.8.0/go.mod h1:QVkue5JL9kW//ek3r6jTKnTFis1tRmNAW2P1shuFdJc=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
 golang.org/x/oauth2 v0.0.0-20190226205417-e64efc72b421/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
 golang.org/x/oauth2 v0.0.0-20190604053449-0f29369cfe45/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
@@ -807,8 +808,8 @@ golang.org/x/text v0.3.4/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.5/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
-golang.org/x/text v0.7.0 h1:4BRB4x83lYWy72KwLD/qYDuTu7q9PjSagHvijDw7cLo=
-golang.org/x/text v0.7.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
+golang.org/x/text v0.8.0 h1:57P1ETyNKtuIjB4SRd15iJxuhj8Gc416Y78H3qgMh68=
+golang.org/x/text v0.8.0/go.mod h1:e1OnstbJyHTd6l/uOt8jFFHp6TRDWZR/bV3emEE/zU8=
 golang.org/x/time v0.0.0-20181108054448-85acf8d2951c/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20190308202827-9d24e82272b4/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20191024005414-555d28b269f0/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
@@ -943,8 +944,8 @@ google.golang.org/genproto v0.0.0-20210108203827-ffc7fda8c3d7/go.mod h1:FWY/as6D
 google.golang.org/genproto v0.0.0-20210226172003-ab064af71705/go.mod h1:FWY/as6DDZQgahTzZj3fqbO1CbirC29ZNUFHwi0/+no=
 google.golang.org/genproto v0.0.0-20210624195500-8bfb893ecb84/go.mod h1:SzzZ/N+nwJDaO1kznhnlzqS8ocJICar6hYhVyhi++24=
 google.golang.org/genproto v0.0.0-20211118181313-81c1377c94b1/go.mod h1:5CzLGKJ67TSI2B9POpiiyGha0AjJvZIUgRMt1dSmuhc=
-google.golang.org/genproto v0.0.0-20221027153422-115e99e71e1c h1:QgY/XxIAIeccR+Ca/rDdKubLIU9rcJ3xfy1DC/Wd2Oo=
-google.golang.org/genproto v0.0.0-20221027153422-115e99e71e1c/go.mod h1:CGI5F/G+E5bKwmfYo09AXuVN4dD894kIKUFmVbP2/Fo=
+google.golang.org/genproto v0.0.0-20230306155012-7f2fa6fef1f4 h1:DdoeryqhaXp1LtT/emMP1BRJPHHKFi5akj/nbx/zNTA=
+google.golang.org/genproto v0.0.0-20230306155012-7f2fa6fef1f4/go.mod h1:NWraEVixdDnqcqQ30jipen1STv2r/n24Wb7twVTGR4s=
 google.golang.org/grpc v1.12.0/go.mod h1:yo6s7OP7yaDglbqo1J04qKzAhqBH6lvTonzMVmEdcZw=
 google.golang.org/grpc v1.19.0/go.mod h1:mqu4LbDTu4XGKhr4mRzUsmM4RtVoemTSY81AxZiDr8c=
 google.golang.org/grpc v1.20.1/go.mod h1:10oTOabMzJvdu6/UiuZezV6QK5dSlG84ov/aaiqXj38=
@@ -967,8 +968,8 @@ google.golang.org/grpc v1.36.0/go.mod h1:qjiiYl8FncCW8feJPdyg3v6XW24KsRHe+dy9BAG
 google.golang.org/grpc v1.38.0/go.mod h1:NREThFqKR1f3iQ6oBuvc5LadQuXVGo9rkm5ZGrQdJfM=
 google.golang.org/grpc v1.40.0/go.mod h1:ogyxbiOoUXAkP+4+xa6PZSE9DZgIHtSpzjDTB9KAK34=
 google.golang.org/grpc v1.42.0/go.mod h1:k+4IHHFw41K8+bbowsex27ge2rCb65oeWqe4jJ590SU=
-google.golang.org/grpc v1.50.1 h1:DS/BukOZWp8s6p4Dt/tOaJaTQyPyOoCcrjroHuCeLzY=
-google.golang.org/grpc v1.50.1/go.mod h1:ZgQEeidpAuNRZ8iRrlBKXZQP1ghovWIVhdJRyCDK+GI=
+google.golang.org/grpc v1.55.0 h1:3Oj82/tFSCeUrRTg/5E/7d/W5A1tj6Ky1ABAuZuv5ag=
+google.golang.org/grpc v1.55.0/go.mod h1:iYEXKGkEBhg1PjZQvoYEVPTDkHo1/bjTnfwTeGONTY8=
 google.golang.org/protobuf v0.0.0-20200109180630-ec00e32a8dfd/go.mod h1:DFci5gLYBciE7Vtevhsrf46CRTquxDuWsQurQQe4oz8=
 google.golang.org/protobuf v0.0.0-20200221191635-4d8936d0db64/go.mod h1:kwYJMbMJ01Woi6D6+Kah6886xMZcty6N08ah7+eCXa0=
 google.golang.org/protobuf v0.0.0-20200228230310-ab0ca4ff8a60/go.mod h1:cfTl7dwQJ+fmap5saPgwCLgHXTUD7jkjRqWcaiX5VyM=
```

### vms/rpcchainvm/grpcutils/server.go
```diff
@@ -25,21 +25,6 @@ const (
 	// of Timeout and if no activity is seen even after that the connection is
 	// closed. grpc-go default 20s
 	defaultServerKeepAliveTimeout = 20 * time.Second
-	// Duration for the maximum amount of time a http2 connection can exist
-	// before sending GOAWAY. Internally in gRPC a +-10% jitter is added to
-	// mitigate retry storms.
-	defaultServerMaxConnectionAge = 10 * time.Minute
-	// After MaxConnectionAge, MaxConnectionAgeGrace specifies the amount of time
-	// between when the server sends a GOAWAY to the client to initiate graceful
-	// shutdown, and when the server closes the connection.
-	//
-	// The server expects that this grace period will allow the client to complete
-	// any ongoing requests, after which it will forcefully terminate the connection.
-	// If a request takes longer than this grace period, it will *fail*.
-	// We *never* want an RPC to live longer than this value.
-	//
-	// invariant: Any value < 1 second will be internally overridden by gRPC.
-	defaultServerMaxConnectionAgeGrace = math.MaxInt64
 )
 
 var DefaultServerOptions = []grpc.ServerOption{
@@ -51,10 +36,8 @@ var DefaultServerOptions = []grpc.ServerOption{
 		PermitWithoutStream: defaultPermitWithoutStream,
 	}),
 	grpc.KeepaliveParams(keepalive.ServerParameters{
-		Time:                  defaultServerKeepAliveInterval,
-		Timeout:               defaultServerKeepAliveTimeout,
-		MaxConnectionAge:      defaultServerMaxConnectionAge,
-		MaxConnectionAgeGrace: defaultServerMaxConnectionAgeGrace,
+		Time:    defaultServerKeepAliveInterval,
+		Timeout: defaultServerKeepAliveTimeout,
 	}),
 }
 
```
