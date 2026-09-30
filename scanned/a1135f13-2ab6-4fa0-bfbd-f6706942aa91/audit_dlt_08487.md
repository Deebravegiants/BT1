# [?] [go.mod] bump for deadlock issue fix (#795)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2023-05-21
Source: https://github.com/sei-protocol/sei-chain/commit/fa6f46cebc470b451cd5f9092d32211406e7f0cc
Type: security-commit

## Details
[go.mod] bump for deadlock issue fix (#795)

## Patch
### go.mod
```diff
@@ -94,7 +94,6 @@ require (
 	github.com/firefart/nonamedreturns v1.0.1 // indirect
 	github.com/fsnotify/fsnotify v1.5.4 // indirect
 	github.com/fzipp/gocyclo v0.5.1 // indirect
-	github.com/ghodss/yaml v1.0.0 // indirect
 	github.com/go-critic/go-critic v0.6.3 // indirect
 	github.com/go-kit/kit v0.12.0 // indirect
 	github.com/go-kit/log v0.2.0 // indirect
@@ -141,7 +140,6 @@ require (
 	github.com/gostaticanalysis/nilerr v0.1.1 // indirect
 	github.com/grpc-ecosystem/go-grpc-middleware v1.3.0 // indirect
 	github.com/grpc-ecosystem/go-grpc-prometheus v1.2.0 // indirect
-	github.com/grpc-ecosystem/grpc-gateway/v2 v2.15.2 // indirect
 	github.com/gsterjov/go-libsecret v0.0.0-20161001094733-a6f4afe4910c // indirect
 	github.com/hashicorp/errwrap v1.0.0 // indirect
 	github.com/hashicorp/go-immutable-radix v1.3.1 // indirect
@@ -276,5 +274,6 @@ replace (
 	github.com/gogo/protobuf => github.com/regen-network/protobuf v1.3.3-alpha.regen.1
 	github.com/keybase/go-keychain => github.com/99designs/go-keychain v0.0.0-20191008050251-8e49817e8af4
 	github.com/tendermint/tendermint => github.com/sei-protocol/sei-tendermint v0.2.17
+	github.com/tendermint/tm-db => github.com/sei-protocol/tm-db v0.0.4
 	google.golang.org/grpc => google.golang.org/grpc v1.33.2
 )
```

### go.sum
```diff
@@ -340,7 +340,6 @@ github.com/fullstorydev/grpcurl v1.6.0/go.mod h1:ZQ+ayqbKMJNhzLmbpCiurTVlaK2M/3n
 github.com/fzipp/gocyclo v0.5.1 h1:L66amyuYogbxl0j2U+vGqJXusPF2IkduvXLnYD5TFgw=
 github.com/fzipp/gocyclo v0.5.1/go.mod h1:rXPyn8fnlpa0R2csP/31uerbiVBugk5whMdlyaLkLoA=
 github.com/gballet/go-libpcsclite v0.0.0-20190607065134-2772fd86a8ff/go.mod h1:x7DCsMOv1taUwEWCzT4cmDeAkigA5/QCwUodaVOe8Ww=
-github.com/ghodss/yaml v1.0.0 h1:wQHKEahhL6wmXdzwWG11gIVCkOv05bNOh+Rxn0yngAk=
 github.com/ghodss/yaml v1.0.0/go.mod h1:4dBDuWmgqj2HViK6kFavaiC9ZROes6MMH2rRYeMEF04=
 github.com/gin-contrib/sse v0.1.0 h1:Y/yl/+YNO8GZSjAhjMsSuLt29uWRFHdHYUb5lYOV9qE=
 github.com/gin-contrib/sse v0.1.0/go.mod h1:RHrZQHXnP2xjPF+u1gW/2HnVO7nvIa9PG3Gm+fLHvGI=
@@ -597,8 +596,6 @@ github.com/grpc-ecosystem/grpc-gateway v1.9.5/go.mod h1:vNeuVxBJEsws4ogUvrchl83t
 github.com/grpc-ecosystem/grpc-gateway v1.12.1/go.mod h1:8XEsbTttt/W+VvjtQhLACqCisSPWTxCZ7sBRjU6iH9c=
 github.com/grpc-ecosystem/grpc-gateway v1.16.0 h1:gmcG1KaJ57LophUzW0Hy8NmPhnMZb4M0+kPpLofRdBo=
 github.com/grpc-ecosystem/grpc-gateway v1.16.0/go.mod h1:BDjrQk3hbvj6Nolgz8mAMFbcEtjT1g+wF4CSlocrBnw=
-github.com/grpc-ecosystem/grpc-gateway/v2 v2.15.2 h1:gDLXvp5S9izjldquuoAhDzccbskOL6tDC5jMSyx3zxE=
-github.com/grpc-ecosystem/grpc-gateway/v2 v2.15.2/go.mod h1:7pdNwVWBBHGiCxa9lAszqCJMbfTISJ7oMftp8+UGV08=
 github.com/gsterjov/go-libsecret v0.0.0-20161001094733-a6f4afe4910c h1:6rhixN/i8ZofjG1Y75iExal34USq5p+wiN1tpie8IrU=
 github.com/gsterjov/go-libsecret v0.0.0-20161001094733-a6f4afe4910c/go.mod h1:NMPJylDgVpX0MLRlPy15sqSwOFv/U1GZ2m21JhFfek0=
 github.com/hashicorp/consul/api v1.3.0/go.mod h1:MmDNSzIMUjNpY/mQ398R4bk2FnqQLoPndWW5VkKPlCE=
@@ -1080,6 +1077,8 @@ github.com/sei-protocol/sei-tm-db v0.0.5 h1:3WONKdSXEqdZZeLuWYfK5hP37TJpfaUa13vA
 github.com/sei-protocol/sei-tm-db v0.0.5/go.mod h1:Cpa6rGyczgthq7/0pI31jys2Fw0Nfrc+/jKdP1prVqY=
 github.com/sei-protocol/sei-wasmd v0.0.2 h1:I0FVTMSWWVVssBQtDgwcDAyDF+ZT2+RqT20ItTBYih8=
 github.com/sei-protocol/sei-wasmd v0.0.2/go.mod h1:IZhrNqhpuoWMIgWR686rzmsTaksn0oylWQG/A0a70ig=
+github.com/sei-protocol/tm-db v0.0.4 h1:7Y4EU62Xzzg6wKAHEotm7SXQR0aPLcGhKHkh3qd0tnk=
+github.com/sei-protocol/tm-db v0.0.4/go.mod h1:PWsIWOTwdwC7Ow/GUvx8HgUJTO691pBuorIQD8JvwAs=
 github.com/sergi/go-diff v1.1.0/go.mod h1:STckp+ISIX8hZLjrqAeVduY0gWCT9IjLuqbuNXdaHfM=
 github.com/shazow/go-diff v0.0.0-20160112020656-b6b7b6733b8c h1:W65qqJCIOVP4jpqPQ0YvHYKwcMEMVWIzWC5iNQQfBTU=
 github.com/shazow/go-diff v0.0.0-20160112020656-b6b7b6733b8c/go.mod h1:/PevMnwAxekIXwN8qQyfc5gl2NlkB3CQlkizAbOkeBs=
@@ -1179,8 +1178,6 @@ github.com/tendermint/crypto v0.0.0-20191022145703-50d29ede1e15 h1:hqAk8riJvK4RM
 github.com/tendermint/crypto v0.0.0-20191022145703-50d29ede1e15/go.mod h1:z4YtwM70uOnk8h0pjJYlj3zdYwi9l03By6iAIF5j/Pk=
 github.com/tendermint/go-amino v0.16.0 h1:GyhmgQKvqF82e2oZeuMSp9JTN0N09emoSZlb2lyGa2E=
 github.com/tendermint/go-amino v0.16.0/go.mod h1:TQU0M1i/ImAo+tYpZi73AU3V/dKeCoMC9Sphe2ZwGME=
-github.com/tendermint/tm-db v0.6.8-0.20220519162814-e24b96538a12 h1:unOeFDC/TV4Oh371XZGmZyfeIzeGfK/JINb0T+6C+QY=
-github.com/tendermint/tm-db v0.6.8-0.20220519162814-e24b96538a12/go.mod h1:PWsIWOTwdwC7Ow/GUvx8HgUJTO691pBuorIQD8JvwAs=
 github.com/tenntenn/modver v1.0.1 h1:2klLppGhDgzJrScMpkj9Ujy3rXPUspSjAcev9tSEBgA=
 github.com/tenntenn/modver v1.0.1/go.mod h1:bePIyQPb7UeioSRkw3Q0XeMhYZSMx9B8ePqg6SAMGH0=
 github.com/tenntenn/text/transform v0.0.0-20200319021203-7eef512accb3 h1:f+jULpRQGxTSkNYKJ51yaw6ChIqO+Je8UqsTKN/cDag=
```
