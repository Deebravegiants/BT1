# [?] fix(relayer): apply jwt-go security patch (#13021)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2023-01-23
Source: https://github.com/taikoxyz/taiko-mono/commit/264968f24024d69a064b27e276e27870fd4c75f6
Type: security-commit

## Details
fix(relayer): apply jwt-go security patch (#13021)

## Patch
### go.mod
```diff
@@ -4,7 +4,7 @@ go 1.19
 
 require (
 	github.com/cyberhorsey/errors v0.0.0-20220929234051-087d6d8bb841
-	github.com/cyberhorsey/webutils v0.0.0-20220929234343-770c4fa3beba
+	github.com/cyberhorsey/webutils v0.0.0-20230119185838-43865c417a79
 	github.com/ethereum/go-ethereum v1.10.25
 	github.com/joho/godotenv v1.4.0
 	github.com/labstack/echo-contrib v0.13.0
@@ -38,7 +38,6 @@ require (
 	github.com/davecgh/go-spew v1.1.1 // indirect
 	github.com/deckarep/golang-set v1.8.0 // indirect
 	github.com/decred/dcrd/dcrec/secp256k1/v4 v4.0.1 // indirect
-	github.com/dgrijalva/jwt-go v3.2.0+incompatible // indirect
 	github.com/docker/distribution v2.8.1+incompatible // indirect
 	github.com/docker/docker v20.10.17+incompatible // indirect
 	github.com/docker/go-connections v0.4.0 // indirect
@@ -51,6 +50,7 @@ require (
 	github.com/go-stack/stack v1.8.0 // indirect
 	github.com/gogo/protobuf v1.3.2 // indirect
 	github.com/golang-jwt/jwt v3.2.2+incompatible // indirect
+	github.com/golang-jwt/jwt/v4 v4.4.3 // indirect
 	github.com/golang/groupcache v0.0.0-20210331224755-41bb18bfe9da // indirect
 	github.com/golang/protobuf v1.5.2 // indirect
 	github.com/google/uuid v1.3.0 // indirect
@@ -62,8 +62,8 @@ require (
 	github.com/magiconair/properties v1.8.6 // indirect
 	github.com/mattn/go-colorable v0.1.12 // indirect
 	github.com/mattn/go-isatty v0.0.14 // indirect
-	github.com/microcosm-cc/bluemonday v1.0.20 // indirect
 	github.com/matttproud/golang_protobuf_extensions v1.0.4 // indirect
+	github.com/microcosm-cc/bluemonday v1.0.20 // indirect
 	github.com/moby/sys/mount v0.3.3 // indirect
 	github.com/moby/sys/mountinfo v0.6.2 // indirect
 	github.com/moby/term v0.0.0-20220808134915-39b0c02b01ae // indirect
```

### go.sum
```diff
@@ -263,8 +263,8 @@ github.com/creack/pty v1.1.11 h1:07n33Z8lZxZ2qwegKbObQohDhXDQxiMMz1NOUGYlesw=
 github.com/creack/pty v1.1.11/go.mod h1:oKZEueFk5CKHvIhNR5MUki03XCEU+Q6VDXinZuGJ33E=
 github.com/cyberhorsey/errors v0.0.0-20220929234051-087d6d8bb841 h1:FaPua89k9KmkkiptlTAmYzcTsn1IFdQsqneuFO6IAu8=
 github.com/cyberhorsey/errors v0.0.0-20220929234051-087d6d8bb841/go.mod h1:qSH/IvpdArCjfny4ODMko/7U0z4JoNIWctgCnUrapnI=
-github.com/cyberhorsey/webutils v0.0.0-20220929234343-770c4fa3beba h1:bNdCrXULXOZo7PLF+Y7u5njDCHr0jgLEKgLsLCFZtck=
-github.com/cyberhorsey/webutils v0.0.0-20220929234343-770c4fa3beba/go.mod h1:SsnedeS2nEcRNpaMO2cQ+0jv86D++V7oMPhF5lKxOwo=
+github.com/cyberhorsey/webutils v0.0.0-20230119185838-43865c417a79 h1:kYxc139hoCg00VynxRxAY4D1ypMrWz83TqchNljIgMM=
+github.com/cyberhorsey/webutils v0.0.0-20230119185838-43865c417a79/go.mod h1:bNNUHadsCy1HleNUToQ/t11vmKI9/+9Taw8K6GyxERo=
 github.com/cyphar/filepath-securejoin v0.2.2/go.mod h1:FpkQEhXnPnOthhzymB7CGsFk2G9VLXONKD9G7QGMM+4=
 github.com/cyphar/filepath-securejoin v0.2.3/go.mod h1:aPGpWjXOXUn2NCNjFvBE6aRxGGx79pTxQpKOJNYHHl4=
 github.com/d2g/dhcp4 v0.0.0-20170904100407-a1d1b6c41b1c/go.mod h1:Ct2BUK8SB0YC1SMSibvLzxjeJLnrYEVLULFNiHY9YfQ=
@@ -284,7 +284,6 @@ github.com/denisenkom/go-mssqldb v0.12.0/go.mod h1:iiK0YP1ZeepvmBQk/QpLEhhTNJgfz
 github.com/denisenkom/go-mssqldb v0.12.2 h1:1OcPn5GBIobjWNd+8yjfHNIaFX14B1pWI3F9HZy5KXw=
 github.com/denverdino/aliyungo v0.0.0-20190125010748-a747050bb1ba/go.mod h1:dV8lFg6daOBZbT6/BDGIz6Y3WFGn8juu6G+CQ6LHtl0=
 github.com/dgrijalva/jwt-go v0.0.0-20170104182250-a601269ab70c/go.mod h1:E3ru+11k8xSBh+hMPgOLZmtrrCbhqsmaPHjLKYnJCaQ=
-github.com/dgrijalva/jwt-go v3.2.0+incompatible h1:7qlOGliEKZXTDg6OTjfoBKDXWrumCAMpl/TFQ4/5kLM=
 github.com/dgrijalva/jwt-go v3.2.0+incompatible/go.mod h1:E3ru+11k8xSBh+hMPgOLZmtrrCbhqsmaPHjLKYnJCaQ=
 github.com/dgryski/go-rendezvous v0.0.0-20200823014737-9f7001d12a5f h1:lO4WD4F/rVNCu3HqELle0jiPLLBs70cWOduZpkS1E78=
 github.com/dgryski/go-sip13 v0.0.0-20181026042036-e10d5fee7954/go.mod h1:vAd38F8PWV+bWy6jNmig1y/TA+kYO4g3RSRF0IAv0no=
@@ -397,7 +396,8 @@ github.com/gogo/protobuf v1.3.2 h1:Ov1cvc58UF3b5XjBnZv7+opcTcQFZebYjWzi34vdm4Q=
 github.com/gogo/protobuf v1.3.2/go.mod h1:P1XiOD3dCwIKUDQYPy72D8LYyHL2YPYrpS2s69NZV8Q=
 github.com/golang-jwt/jwt v3.2.2+incompatible h1:IfV12K8xAKAnZqdXVzCZ+TOjboZ2keLg81eXfW3O+oY=
 github.com/golang-jwt/jwt v3.2.2+incompatible/go.mod h1:8pz2t5EyA70fFQQSrl6XZXzqecmYZeUEB8OUGHkxJ+I=
-github.com/golang-jwt/jwt/v4 v4.3.0 h1:kHL1vqdqWNfATmA0FNMdmZNMyZI1U6O31X4rlIPoBog=
+github.com/golang-jwt/jwt/v4 v4.4.3 h1:Hxl6lhQFj4AnOX6MLrsCb/+7tCj7DxP7VA+2rDIq5AU=
+github.com/golang-jwt/jwt/v4 v4.4.3/go.mod h1:m21LjoU+eqJr34lmDMbreY2eSTRJ1cv77w39/MY0Ch0=
 github.com/golang-sql/civil v0.0.0-20190719163853-cb61b32ac6fe/go.mod h1:8vg3r2VgvsThLBIFL93Qb5yWzgyZWhEmBwUJWevAkK0=
 github.com/golang-sql/civil v0.0.0-20220223132316-b832511892a9 h1:au07oEsX2xN0ktxqI+Sida1w446QrXBRJ0nee3SNZlA=
 github.com/golang-sql/civil v0.0.0-20220223132316-b832511892a9/go.mod h1:8vg3r2VgvsThLBIFL93Qb5yWzgyZWhEmBwUJWevAkK0=
```
