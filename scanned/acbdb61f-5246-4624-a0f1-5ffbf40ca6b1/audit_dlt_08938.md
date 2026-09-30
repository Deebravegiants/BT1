# [?] chore: remove packages with vulnerabilities (#1184)

## Summary
Severity: Unknown
Chain: Axelar
Component: axelarnetwork/axelar-core
Published: 2022-01-05
Source: https://github.com/axelarnetwork/axelar-core/commit/127e43c8647081e31cf2238195205a940cd1c62c
Type: security-commit

## Details
chore: remove packages with vulnerabilities (#1184)

## Patch
### go.mod
```diff
@@ -148,6 +148,10 @@ require (
 
 replace google.golang.org/grpc => google.golang.org/grpc v1.33.2
 
+replace github.com/opencontainers/image-spec v1.0.1 => github.com/opencontainers/image-spec v1.0.2
+
+replace github.com/opencontainers/runc v1.0.2 => github.com/opencontainers/runc v1.0.3
+
 replace github.com/gogo/protobuf => github.com/regen-network/protobuf v1.3.3-alpha.regen.1
 
 replace github.com/keybase/go-keychain => github.com/99designs/go-keychain v0.0.0-20191008050251-8e49817e8af4 // https://github.com/axelarnetwork/axelar-core/issues/36
```

### go.sum
```diff
@@ -874,11 +874,11 @@ github.com/op/go-logging v0.0.0-20160315200505-970db520ece7/go.mod h1:HzydrMdWEr
 github.com/opencontainers/go-digest v1.0.0-rc1/go.mod h1:cMLVZDEM3+U2I4VmLI6N8jQYUd2OVphdqWwCJHrFt2s=
 github.com/opencontainers/go-digest v1.0.0 h1:apOUWs51W5PlhuyGyz9FCeeBIOUDA/6nW8Oi/yOhh5U=
 github.com/opencontainers/go-digest v1.0.0/go.mod h1:0JzlMkj0TRzQZfJkVvzbP0HBR3IKzErnv2BNG4W4MAM=
-github.com/opencontainers/image-spec v1.0.1 h1:JMemWkRwHx4Zj+fVxWoMCFm/8sYGGrUVojFA6h/TRcI=
-github.com/opencontainers/image-spec v1.0.1/go.mod h1:BtxoFyWECRxE4U/7sNtV5W15zMzWCbyJoFRP3s7yZA0=
+github.com/opencontainers/image-spec v1.0.2 h1:9yCKha/T5XdGtO0q9Q9a6T5NUCsTn/DrBg0D7ufOcFM=
+github.com/opencontainers/image-spec v1.0.2/go.mod h1:BtxoFyWECRxE4U/7sNtV5W15zMzWCbyJoFRP3s7yZA0=
 github.com/opencontainers/runc v0.1.1/go.mod h1:qT5XzbpPznkRYVz/mWwUaVBUv2rmF59PVA73FjuZG0U=
-github.com/opencontainers/runc v1.0.2 h1:opHZMaswlyxz1OuGpBE53Dwe4/xF7EZTY0A2L/FpCOg=
-github.com/opencontainers/runc v1.0.2/go.mod h1:aTaHFFwQXuA71CiyxOdFFIorAoemI04suvGRQFzWTD0=
+github.com/opencontainers/runc v1.0.3 h1:1hbqejyQWCJBvtKAfdO0b1FmaEf2z/bxnjqbARass5k=
+github.com/opencontainers/runc v1.0.3/go.mod h1:aTaHFFwQXuA71CiyxOdFFIorAoemI04suvGRQFzWTD0=
 github.com/opencontainers/runtime-spec v1.0.3-0.20210326190908-1c3f411f0417/go.mod h1:jwyrGlmzljRJv/Fgzds9SsS/C5hL+LL3ko9hs6T5lQ0=
 github.com/opencontainers/selinux v1.8.2/go.mod h1:MUIHuUEvKB1wtJjQdOyYRgOnLD2xAPP8dBsCoU0KuF8=
 github.com/opentracing-contrib/go-observer v0.0.0-20170622124052-a52f23424492/go.mod h1:Ngi6UdF0k5OKD5t5wlmGhe/EDKPoUM3BXZSSfIuJbis=
```
