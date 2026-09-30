# [?] fix: resolving dependabot vulnerabilities. (#8643)

## Summary
Severity: Unknown
Chain: Kroma
Component: kroma-network/kroma
Published: 2023-12-15
Source: https://github.com/kroma-network/kroma/commit/6d78aa0974e1b4b03ee1629c75506f342e1bc071
Type: security-commit

## Details
fix: resolving dependabot vulnerabilities. (#8643)

* resolving dependabot vulnerabilities.
setting go-ethereum v.1.13.5 everywhere and grpc to v1.56.3

* fixing sum sha

## Patch
### op-exporter/go.mod
```diff
@@ -3,7 +3,7 @@ module github.com/ethereum-optimism/optimism/op-exporter
 go 1.20
 
 require (
-	github.com/ethereum/go-ethereum v1.12.1
+	github.com/ethereum/go-ethereum v1.13.5
 	github.com/prometheus/client_golang v1.14.0
 	github.com/sirupsen/logrus v1.7.0
 	github.com/ybbus/jsonrpc v2.1.2+incompatible
@@ -20,7 +20,7 @@ require (
 	github.com/davecgh/go-spew v1.1.1 // indirect
 	github.com/go-logr/logr v0.4.0 // indirect
 	github.com/gogo/protobuf v1.3.2 // indirect
-	github.com/golang/protobuf v1.5.2 // indirect
+	github.com/golang/protobuf v1.5.3 // indirect
 	github.com/google/go-cmp v0.5.9 // indirect
 	github.com/google/gofuzz v1.1.1-0.20200604201612-c04b05f3adfa // indirect
 	github.com/googleapis/gnostic v0.4.1 // indirect
```

### op-exporter/go.sum
```diff
@@ -56,8 +56,8 @@ github.com/elazarl/goproxy v0.0.0-20180725130230-947c36da3153/go.mod h1:/Zj4wYkg
 github.com/emicklei/go-restful v0.0.0-20170410110728-ff4f55a20633/go.mod h1:otzb+WCGbkyDHkqmQmT5YD2WR4BBwUdeQoFo8l/7tVs=
 github.com/envoyproxy/go-control-plane v0.9.1-0.20191026205805-5f8ba28d4473/go.mod h1:YTl/9mNaCwkRvm6d1a2C3ymFceY/DCBVvsKhRF0iEA4=
 github.com/envoyproxy/protoc-gen-validate v0.1.0/go.mod h1:iSmxcyjqTsJpI2R4NaDN7+kN2VEUnK/pcBlmesArF7c=
-github.com/ethereum/go-ethereum v1.12.1 h1:1kXDPxhLfyySuQYIfRxVBGYuaHdxNNxevA73vjIwsgk=
-github.com/ethereum/go-ethereum v1.12.1/go.mod h1:zKetLweqBR8ZS+1O9iJWI8DvmmD2NzD19apjEWDCsnw=
+github.com/ethereum/go-ethereum v1.13.5 h1:U6TCRciCqZRe4FPXmy1sMGxTfuk8P7u2UoinF3VbaFk=
+github.com/ethereum/go-ethereum v1.13.5/go.mod h1:yMTu38GSuyxaYzQMViqNmQ1s3cE84abZexQmTgenWk0=
 github.com/evanphx/json-patch v4.9.0+incompatible/go.mod h1:50XU6AFN0ol/bzJsmQLiYLvXMP4fmwYFNcr97nuDLSk=
 github.com/form3tech-oss/jwt-go v3.2.2+incompatible/go.mod h1:pbq4aXjuKjdthFRnoDwaVPLA+WlJuPGy+QneDUgJi2k=
 github.com/fsnotify/fsnotify v1.4.7/go.mod h1:jwhsz4b93w/PPRr/qN1Yymfu8t87LnFCMoQvtojpjFo=
@@ -102,8 +102,9 @@ github.com/golang/protobuf v1.4.1/go.mod h1:U8fpvMrcmy5pZrNK1lt4xCsGvpyWQ/VVv6QD
 github.com/golang/protobuf v1.4.2/go.mod h1:oDoupMAO8OvCJWAcko0GGGIgR6R6ocIYbsSw735rRwI=
 github.com/golang/protobuf v1.4.3/go.mod h1:oDoupMAO8OvCJWAcko0GGGIgR6R6ocIYbsSw735rRwI=
 github.com/golang/protobuf v1.5.0/go.mod h1:FsONVRAS9T7sI+LIUmWTfcYkHO4aIWwzhcaSAoJOfIk=
-github.com/golang/protobuf v1.5.2 h1:ROPKBNFfQgOUMifHyP+KYbvpjbdoFNs+aK7DXlji0Tw=
 github.com/golang/protobuf v1.5.2/go.mod h1:XVQd3VNwM+JqD3oG2Ue2ip4fOMUkwXdXDdiuN0vRsmY=
+github.com/golang/protobuf v1.5.3 h1:KhyjKVUg7Usr/dYsdSqoFveMYd5ko72D+zANwlG1mmg=
+github.com/golang/protobuf v1.5.3/go.mod h1:XVQd3VNwM+JqD3oG2Ue2ip4fOMUkwXdXDdiuN0vRsmY=
 github.com/google/btree v0.0.0-20180813153112-4030bb1f1f0c/go.mod h1:lNA+9X1NB3Zf8V7Ke586lFgjr2dZNuvo3lPJSGZ5JPQ=
 github.com/google/btree v1.0.0/go.mod h1:lNA+9X1NB3Zf8V7Ke586lFgjr2dZNuvo3lPJSGZ5JPQ=
 github.com/google/go-cmp v0.2.0/go.mod h1:oXzfMopK8JAjlY9xF4vHSVASa0yLyX7SntLO5aqRK0M=
@@ -212,7 +213,7 @@ github.com/stretchr/testify v1.3.0/go.mod h1:M5WIy9Dh21IEIfnGCwXGc5bZfKNJtfHm1UV
 github.com/stretchr/testify v1.4.0/go.mod h1:j7eGeouHqKxXV5pUuKE4zz7dFj8WfuZ+81PSLYec5m4=
 github.com/stretchr/testify v1.5.1/go.mod h1:5W2xD1RspED5o8YsWQXVCued0rvSQ+mT+I5cxcmMvtA=
 github.com/stretchr/testify v1.6.1/go.mod h1:6Fq8oRcR53rry900zMqJjRRixrwX3KX962/h/Wwjteg=
-github.com/stretchr/testify v1.8.1 h1:w7B6lhMri9wdJUVmEZPGGhZzrYTPvgJArz7wNPgYKsk=
+github.com/stretchr/testify v1.8.4 h1:CcVxjf3Q8PM0mHUKJCdn+eZZtm5yQwehR5yeSVQQcUk=
 github.com/ybbus/jsonrpc v2.1.2+incompatible h1:V4mkE9qhbDQ92/MLMIhlhMSbz8jNXdagC3xBR5NDwaQ=
 github.com/ybbus/jsonrpc v2.1.2+incompatible/go.mod h1:XJrh1eMSzdIYFbM08flv0wp5G35eRniyeGut1z+LSiE=
 github.com/yuin/goldmark v1.1.27/go.mod h1:3hX8gzYuyVAZsxl0MRgGTJEmQBFcNTphYh9decYSb74=
```

### op-ufm/go.mod
```diff
@@ -8,7 +8,7 @@ require (
 	cloud.google.com/go/kms v1.12.1
 	github.com/BurntSushi/toml v1.3.2
 	github.com/ethereum-optimism/optimism v1.2.0
-	github.com/ethereum/go-ethereum v1.13.1
+	github.com/ethereum/go-ethereum v1.13.5
 	github.com/gorilla/mux v1.8.0
 	github.com/pkg/errors v0.9.1
 	github.com/prometheus/client_golang v1.17.0
@@ -21,22 +21,23 @@ require (
 	cloud.google.com/go/iam v1.1.0 // indirect
 	github.com/DataDog/zstd v1.5.2 // indirect
 	github.com/Microsoft/go-winio v0.6.1 // indirect
-	github.com/VictoriaMetrics/fastcache v1.10.0 // indirect
+	github.com/VictoriaMetrics/fastcache v1.12.1 // indirect
 	github.com/beorn7/perks v1.0.1 // indirect
 	github.com/bits-and-blooms/bitset v1.7.0 // indirect
 	github.com/btcsuite/btcd/btcec/v2 v2.2.0 // indirect
 	github.com/cespare/xxhash/v2 v2.2.0 // indirect
 	github.com/cockroachdb/errors v1.9.1 // indirect
 	github.com/cockroachdb/logtags v0.0.0-20230118201751-21c54148d20b // indirect
-	github.com/cockroachdb/pebble v0.0.0-20230906160148-46873a6a7a06 // indirect
+	github.com/cockroachdb/pebble v0.0.0-20230928194634-aa077af62593 // indirect
 	github.com/cockroachdb/redact v1.1.3 // indirect
+	github.com/cockroachdb/tokenbucket v0.0.0-20230807174530-cc333fc44b06 // indirect
 	github.com/consensys/bavard v0.1.13 // indirect
-	github.com/consensys/gnark-crypto v0.12.0 // indirect
+	github.com/consensys/gnark-crypto v0.12.1 // indirect
 	github.com/cpuguy83/go-md2man/v2 v2.0.2 // indirect
-	github.com/crate-crypto/go-kzg-4844 v0.3.0 // indirect
+	github.com/crate-crypto/go-kzg-4844 v0.7.0 // indirect
 	github.com/deckarep/golang-set/v2 v2.1.0 // indirect
 	github.com/decred/dcrd/dcrec/secp256k1/v4 v4.2.0 // indirect
-	github.com/ethereum/c-kzg-4844 v0.3.1 // indirect
+	github.com/ethereum/c-kzg-4844 v0.4.0 // indirect
 	github.com/fsnotify/fsnotify v1.6.0 // indirect
 	github.com/getsentry/sentry-go v0.18.0 // indirect
 	github.com/go-ole/go-ole v1.2.6 // indirect
@@ -71,7 +72,6 @@ require (
 	github.com/syndtr/goleveldb v1.0.1-0.20220614013038-64ee5596c38a // indirect
 	github.com/tklauser/go-sysconf v0.3.12 // indirect
 	github.com/tklauser/numcpus v0.6.1 // indirect
-	github.com/urfave/cli v1.22.9 // indirect
 	github.com/urfave/cli/v2 v2.25.7 // indirect
 	github.com/xrash/smetrics v0.0.0-20201216005158-039620a65673 // indirect
 	github.com/yusufpapurcu/wmi v1.2.2 // indirect
@@ -90,8 +90,7 @@ require (
 	google.golang.org/genproto v0.0.0-20230706204954-ccb25ca9f130 // indirect
 	google.golang.org/genproto/googleapis/api v0.0.0-20230706204954-ccb25ca9f130 // indirect
 	google.golang.org/genproto/googleapis/rpc v0.0.0-20230711160842-782d3b101e98 // indirect
-	google.golang.org/grpc v1.56.2 // indirect
+	google.golang.org/grpc v1.56.3 // indirect
 	google.golang.org/protobuf v1.31.0 // indirect
-	gopkg.in/natefinch/npipe.v2 v2.0.0-20160621034901-c1b8fa8bdcce // indirect
 	rsc.io/tmplfunc v0.0.3 // indirect
 )
```

### op-ufm/go.sum
```diff
@@ -1,6 +1,7 @@
 cloud.google.com/go v0.26.0/go.mod h1:aQUYkXzVsufM+DwF1aE+0xfcU+56JwCaLick0ClmMTw=
 cloud.google.com/go v0.34.0/go.mod h1:aQUYkXzVsufM+DwF1aE+0xfcU+56JwCaLick0ClmMTw=
 cloud.google.com/go v0.110.4 h1:1JYyxKMN9hd5dR2MYTPWkGUgcoxVVhg0LKNKEo0qvmk=
+cloud.google.com/go v0.110.4/go.mod h1:+EYjdK8e5RME/VY/qLCAtuyALQ9q67dvuum8i+H5xsI=
 cloud.google.com/go/compute v1.20.1 h1:6aKEtlUiwEpJzM001l0yFkpXmUVXaN8W+fbkb2AZNbg=
 cloud.google.com/go/compute v1.20.1/go.mod h1:4tCnrn48xsqlwSAiLf1HXMQk8CONslYbdiEZc9FEIbM=
 cloud.google.com/go/compute/metadata v0.2.3 h1:mg4jlk7mCAj6xXp9UJ4fjI9VUI5rubuGBW5aJ7UnBMY=
@@ -21,11 +22,12 @@ github.com/Joker/hpp v1.0.0/go.mod h1:8x5n+M1Hp5hC0g8okX3sR3vFQwynaX/UgSOM9MeBKz
 github.com/Microsoft/go-winio v0.6.1 h1:9/kr64B9VUZrLm5YYwbGtUJnMgqWVOdUAXu6Migciow=
 github.com/Microsoft/go-winio v0.6.1/go.mod h1:LRdKpFKfdobln8UmuiYcKPot9D2v6svN5+sAH+4kjUM=
 github.com/Shopify/goreferrer v0.0.0-20181106222321-ec9c9a553398/go.mod h1:a1uqRtAwp2Xwc6WNPJEufxJ7fx3npB4UV/JOLmbu5I0=
-github.com/VictoriaMetrics/fastcache v1.10.0 h1:5hDJnLsKLpnUEToub7ETuRu8RCkb40woBZAUiKonXzY=
-github.com/VictoriaMetrics/fastcache v1.10.0/go.mod h1:tjiYeEfYXCqacuvYw/7UoDIeJaNxq6132xHICNP77w8=
+github.com/VictoriaMetrics/fastcache v1.12.1 h1:i0mICQuojGDL3KblA7wUNlY5lOK6a4bwt3uRKnkZU40=
+github.com/VictoriaMetrics/fastcache v1.12.1/go.mod h1:tX04vaqcNoQeGLD+ra5pU5sWkuxnzWhEzLwhP9w653o=
 github.com/ajg/form v1.5.1/go.mod h1:uL1WgH+h2mgNtvBq0339dVnzXdBETtL2LeUXaIv25UY=
-github.com/allegro/bigcache v1.2.1-0.20190218064605-e24eb225f156 h1:eMwmnE/GDgah4HI848JfFxHt+iPb26b4zyfspmqY0/8=
 github.com/allegro/bigcache v1.2.1-0.20190218064605-e24eb225f156/go.mod h1:Cb/ax3seSYIx7SuZdm2G2xzfwmv3TPSk2ucNfQESPXM=
+github.com/allegro/bigcache v1.2.1 h1:hg1sY1raCwic3Vnsvje6TT7/pnZba83LeFck5NrFKSc=
+github.com/allegro/bigcache v1.2.1/go.mod h1:Cb/ax3seSYIx7SuZdm2G2xzfwmv3TPSk2ucNfQESPXM=
 github.com/antihax/optional v1.0.0/go.mod h1:uupD/76wgC+ih3iEmQUL+0Ugr19nfwCT1kdvxnR2qWY=
 github.com/armon/consul-api v0.0.0-20180202201655-eb2c6b5be1b6/go.mod h1:grANhF5doyWs3UAsr3K4I6qtAmlQcZDesFNEHPZAzj8=
 github.com/aymerick/raymond v2.0.3-0.20180322193309-b565731e1464+incompatible/go.mod h1:osfaiScAUVup+UC9Nfq76eWqDhXlp+4UYaA8uhTBO6g=
@@ -37,9 +39,9 @@ github.com/btcsuite/btcd v0.23.3 h1:4KH/JKy9WiCd+iUS9Mu0Zp7Dnj17TGdKrg9xc/FGj24=
 github.com/btcsuite/btcd/btcec/v2 v2.2.0 h1:fzn1qaOt32TuLjFlkzYSsBC35Q3KUjT1SwPxiMSCF5k=
 github.com/btcsuite/btcd/btcec/v2 v2.2.0/go.mod h1:U7MHm051Al6XmscBQ0BoNydpOTsFAn707034b5nY8zU=
 github.com/btcsuite/btcd/chaincfg/chainhash v1.0.1 h1:q0rUy8C/TYNBQS1+CGKw68tLOFYSNEs0TFnxxnS9+4U=
+github.com/btcsuite/btcd/chaincfg/chainhash v1.0.1/go.mod h1:7SFka0XMvUgj3hfZtydOrQY2mwhPclbT2snogU7SQQc=
 github.com/census-instrumentation/opencensus-proto v0.2.1/go.mod h1:f6KPmirojxKA12rnyqOA5BBL4O983OfeGPqjHWSTneU=
 github.com/cespare/xxhash/v2 v2.1.1/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
-github.com/cespare/xxhash/v2 v2.1.2/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
 github.com/cespare/xxhash/v2 v2.2.0 h1:DC2CZ1Ep5Y4k3ZQ899DldepgrayRUGE6BBZ/cd9Cj44=
 github.com/cespare/xxhash/v2 v2.2.0/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
 github.com/chzyer/logex v1.1.10/go.mod h1:+Ywpsq7O8HXn0nuIou7OrIPyXbp3wmkHB+jjWRnGsAI=
@@ -52,42 +54,41 @@ github.com/cncf/udpa/go v0.0.0-20210930031921-04548b0d99d4/go.mod h1:6pvJx4me5XP
 github.com/cncf/xds/go v0.0.0-20210805033703-aa0b78936158/go.mod h1:eXthEFrGJvWHgFFCl3hGmgk+/aYT6PnTQLykKQRLhEs=
 github.com/cncf/xds/go v0.0.0-20210922020428-25de7278fc84/go.mod h1:eXthEFrGJvWHgFFCl3hGmgk+/aYT6PnTQLykKQRLhEs=
 github.com/cncf/xds/go v0.0.0-20211011173535-cb28da3451f1/go.mod h1:eXthEFrGJvWHgFFCl3hGmgk+/aYT6PnTQLykKQRLhEs=
-github.com/cockroachdb/datadriven v1.0.2 h1:H9MtNqVoVhvd9nCBwOyDjUEdZCREqbIdCJD93PBm/jA=
 github.com/cockroachdb/datadriven v1.0.2/go.mod h1:a9RdTaap04u637JoCzcUoIcDmvwSUtcUFtT/C3kJlTU=
+github.com/cockroachdb/datadriven v1.0.3-0.20230413201302-be42291fc80f h1:otljaYPt5hWxV3MUfO5dFPFiOXg9CyG5/kCfayTqsJ4=
+github.com/cockroachdb/datadriven v1.0.3-0.20230413201302-be42291fc80f/go.mod h1:a9RdTaap04u637JoCzcUoIcDmvwSUtcUFtT/C3kJlTU=
 github.com/cockroachdb/errors v1.9.1 h1:yFVvsI0VxmRShfawbt/laCIDy/mtTqqnvoNgiy5bEV8=
 github.com/cockroachdb/errors v1.9.1/go.mod h1:2sxOtL2WIc096WSZqZ5h8fa17rdDq9HZOZLBCor4mBk=
 github.com/cockroachdb/logtags v0.0.0-20211118104740-dabe8e521a4f/go.mod h1:Vz9DsVWQQhf3vs21MhPMZpMGSht7O/2vFW2xusFUVOs=
 github.com/cockroachdb/logtags v0.0.0-20230118201751-21c54148d20b h1:r6VH0faHjZeQy818SGhaone5OnYfxFR/+AzdY3sf5aE=
 github.com/cockroachdb/logtags v0.0.0-20230118201751-21c54148d20b/go.mod h1:Vz9DsVWQQhf3vs21MhPMZpMGSht7O/2vFW2xusFUVOs=
-github.com/cockroachdb/pebble v0.0.0-20230209160836-829675f94811 h1:ytcWPaNPhNoGMWEhDvS3zToKcDpRsLuRolQJBVGdozk=
-github.com/cockroachdb/pebble v0.0.0-20230209160836-829675f94811/go.mod h1:Nb5lgvnQ2+oGlE/EyZy4+2/CxRh9KfvCXnag1vtpxVM=
-github.com/cockroachdb/pebble v0.0.0-20230906160148-46873a6a7a06 h1:T+Np/xtzIjYM/P5NAw0e2Rf1FGvzDau1h54MKvx8G7w=
-github.com/cockroachdb/pebble v0.0.0-20230906160148-46873a6a7a06/go.mod h1:bynZ3gvVyhlvjLI7PT6dmZ7g76xzJ7HpxfjgkzCGz6s=
+github.com/cockroachdb/pebble v0.0.0-20230928194634-aa077af62593 h1:aPEJyR4rPBvDmeyi+l/FS/VtA00IWvjeFvjen1m1l1A=
+github.com/cockroachdb/pebble v0.0.0-20230928194634-aa077af62593/go.mod h1:6hk1eMY/u5t+Cf18q5lFMUA1Rc+Sm5I6Ra1QuPyxXCo=
 github.com/cockroachdb/redact v1.1.3 h1:AKZds10rFSIj7qADf0g46UixK8NNLwWTNdCIGS5wfSQ=
 github.com/cockroachdb/redact v1.1.3/go.mod h1:BVNblN9mBWFyMyqK1k3AAiSxhvhfK2oOZZ2lK+dpvRg=
+github.com/cockroachdb/tokenbucket v0.0.0-20230807174530-cc333fc44b06 h1:zuQyyAKVxetITBuuhv3BI9cMrmStnpT18zmgmTxunpo=
+github.com/cockroachdb/tokenbucket v0.0.0-20230807174530-cc333fc44b06/go.mod h1:7nc4anLGjupUW/PeY5qiNYsdNXj7zopG+eqsS7To5IQ=
 github.com/codegangsta/inject v0.0.0-20150114235600-33e0aa1cb7c0/go.mod h1:4Zcjuz89kmFXt9morQgcfYZAYZ5n8WHjt81YYWIwtTM=
 github.com/consensys/bavard v0.1.13 h1:oLhMLOFGTLdlda/kma4VOJazblc7IM5y5QPd2A/YjhQ=
 github.com/consensys/bavard v0.1.13/go.mod h1:9ItSMtA/dXMAiL7BG6bqW2m3NdSEObYWoH223nGHukI=
-github.com/consensys/gnark-crypto v0.12.0 h1:1OnSpOykNkUIBIBJKdhwy2p0JlW5o+Az02ICzZmvvdg=
-github.com/consensys/gnark-crypto v0.12.0/go.mod h1:v2Gy7L/4ZRosZ7Ivs+9SfUDr0f5UlG+EM5t7MPHiLuY=
+github.com/consensys/gnark-crypto v0.12.1 h1:lHH39WuuFgVHONRl3J0LRBtuYdQTumFSDtJF7HpyG8M=
+github.com/consensys/gnark-crypto v0.12.1/go.mod h1:v2Gy7L/4ZRosZ7Ivs+9SfUDr0f5UlG+EM5t7MPHiLuY=
 github.com/coreos/etcd v3.3.10+incompatible/go.mod h1:uF7uidLiAD3TWHmW31ZFd/JWoc32PjwdhPthX9715RE=
 github.com/coreos/go-etcd v2.0.0+incompatible/go.mod h1:Jez6KQU2B/sWsbdaef3ED8NzMklzPG4d5KIOhIy30Tk=
 github.com/coreos/go-semver v0.2.0/go.mod h1:nnelYz7RCh+5ahJtPPxZlU+153eP4D4r3EedlOD2RNk=
 github.com/cpuguy83/go-md2man v1.0.10/go.mod h1:SmD6nW6nTyfqj6ABTjUi3V3JVMnlJmwcJI5acqYI6dE=
-github.com/cpuguy83/go-md2man/v2 v2.0.0-20190314233015-f79a8a8ca69d/go.mod h1:maD7wRr/U5Z6m/iR4s+kqSMx2CaBsrgA7czyZG/E6dU=
 github.com/cpuguy83/go-md2man/v2 v2.0.2 h1:p1EgwI/C7NhT0JmVkwCD2ZBK8j4aeHQX2pMHHBfMQ6w=
 github.com/cpuguy83/go-md2man/v2 v2.0.2/go.mod h1:tgQtvFlXSQOSOSIRvRPT7W67SCa46tRHOmNcaadrF8o=
-github.com/crate-crypto/go-kzg-4844 v0.3.0 h1:UBlWE0CgyFqqzTI+IFyCzA7A3Zw4iip6uzRv5NIXG0A=
-github.com/crate-crypto/go-kzg-4844 v0.3.0/go.mod h1:SBP7ikXEgDnUPONgm33HtuDZEDtWa3L4QtN1ocJSEQ4=
+github.com/crate-crypto/go-kzg-4844 v0.7.0 h1:C0vgZRk4q4EZ/JgPfzuSoxdCq3C3mOZMBShovmncxvA=
+github.com/crate-crypto/go-kzg-4844 v0.7.0/go.mod h1:1kMhvPgI0Ky3yIa+9lFySEBUBXkYxeOi8ZF1sYioxhc=
 github.com/creack/pty v1.1.9/go.mod h1:oKZEueFk5CKHvIhNR5MUki03XCEU+Q6VDXinZuGJ33E=
 github.com/davecgh/go-spew v1.1.0/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
 github.com/davecgh/go-spew v1.1.1 h1:vj9j/u1bqnvCEfJOwUhtlOARqs3+rkHYY13jYWTU97c=
 github.com/davecgh/go-spew v1.1.1/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
 github.com/deckarep/golang-set/v2 v2.1.0 h1:g47V4Or+DUdzbs8FxCCmgb6VYd+ptPAngjM6dtGktsI=
 github.com/deckarep/golang-set/v2 v2.1.0/go.mod h1:VAky9rY/yGXJOLEDv3OMci+7wtDpOF4IN+y82NBOac4=
-github.com/decred/dcrd/crypto/blake256 v1.0.0 h1:/8DMNYp9SGi5f0w7uCm6d6M4OU2rGFK09Y2A4Xv7EE0=
-github.com/decred/dcrd/dcrec/secp256k1/v4 v4.1.0 h1:HbphB4TFFXpv7MNrT52FGrrgVXF1owhMVTHFZIlnvd4=
-github.com/decred/dcrd/dcrec/secp256k1/v4 v4.1.0/go.mod h1:DZGJHZMqrU4JJqFAWUS2UO1+lbSKsdiOoYi9Zzey7Fc=
+github.com/decred/dcrd/crypto/blake256 v1.0.1 h1:7PltbUIQB7u/FfZ39+DGa/ShuMyJ5ilcvdfma9wOH6Y=
+github.com/decred/dcrd/crypto/blake256 v1.0.1/go.mod h1:2OfgNZ5wDpcsFmHmCK5gZTPcCXqlm2ArzUIkw9czNJo=
 github.com/decred/dcrd/dcrec/secp256k1/v4 v4.2.0 h1:8UrgZ3GkP4i/CLijOJx79Yu+etlyjdBU4sfcs2WYQMs=
 github.com/decred/dcrd/dcrec/secp256k1/v4 v4.2.0/go.mod h1:v57UDF4pDQJcEfFUCRop3lJL149eHGSe9Jvczhzjo/0=
 github.com/dgraph-io/badger v1.6.0/go.mod h1:zwt7syl517jmP8s94KqSxTlM6IMsdhYy6psNgSztDR4=
@@ -104,26 +105,22 @@ github.com/envoyproxy/protoc-gen-validate v0.1.0/go.mod h1:iSmxcyjqTsJpI2R4NaDN7
 github.com/etcd-io/bbolt v1.3.3/go.mod h1:ZF2nL25h33cCyBtcyWeZ2/I3HQOfTP+0PIEvHjkjCrw=
 github.com/ethereum-optimism/optimism v1.2.0 h1:wlVqKHj6+HCMrXRskLM7b45zcdqSHCsVk0Kmg+ViCS8=
 github.com/ethereum-optimism/optimism v1.2.0/go.mod h1:y1J1a0BkbJ5MTImx1Ayk2syTXZEoFucRAsBpdzbn0Qk=
-github.com/ethereum-optimism/optimism/op-service v0.10.14 h1:MC+rVwtPfX1aPAKA3855DQaCnhjjp4uFcSr8PY7HmaE=
-github.com/ethereum-optimism/optimism/op-service v0.10.14/go.mod h1:8ay6Bs3YHaX+FbJRUGSbxBnXRtEbKXNHMhtJqATrBmY=
-github.com/ethereum/c-kzg-4844 v0.3.0 h1:3Y3hD6l5i0dEYsBL50C+Om644kve3pNqoAcvE26o9zI=
-github.com/ethereum/c-kzg-4844 v0.3.0/go.mod h1:WI2Nd82DMZAAZI1wV2neKGost9EKjvbpQR9OqE5Qqa8=
-github.com/ethereum/c-kzg-4844 v0.3.1 h1:sR65+68+WdnMKxseNWxSJuAv2tsUrihTpVBTfM/U5Zg=
-github.com/ethereum/c-kzg-4844 v0.3.1/go.mod h1:VewdlzQmpT5QSrVhbBuGoCdFJkpaJlO1aQputP83wc0=
-github.com/ethereum/go-ethereum v1.12.1 h1:1kXDPxhLfyySuQYIfRxVBGYuaHdxNNxevA73vjIwsgk=
-github.com/ethereum/go-ethereum v1.12.1/go.mod h1:zKetLweqBR8ZS+1O9iJWI8DvmmD2NzD19apjEWDCsnw=
-github.com/ethereum/go-ethereum v1.13.1 h1:UF2FaUKPIy5jeZk3X06ait3y2Q4wI+vJ1l7+UARp+60=
-github.com/ethereum/go-ethereum v1.13.1/go.mod h1:xHQKzwkHSl0gnSjZK1mWa06XEdm9685AHqhRknOzqGQ=
+github.com/ethereum/c-kzg-4844 v0.4.0 h1:3MS1s4JtA868KpJxroZoepdV0ZKBp3u/O5HcZ7R3nlY=
+github.com/ethereum/c-kzg-4844 v0.4.0/go.mod h1:VewdlzQmpT5QSrVhbBuGoCdFJkpaJlO1aQputP83wc0=
+github.com/ethereum/go-ethereum v1.13.5 h1:U6TCRciCqZRe4FPXmy1sMGxTfuk8P7u2UoinF3VbaFk=
+github.com/ethereum/go-ethereum v1.13.5/go.mod h1:yMTu38GSuyxaYzQMViqNmQ1s3cE84abZexQmTgenWk0=
 github.com/fasthttp-contrib/websocket v0.0.0-20160511215533-1f3b11f56072/go.mod h1:duJ4Jxv5lDcvg4QuQr0oowTf7dz4/CR8NtyCooz9HL8=
 github.com/fatih/structs v1.1.0/go.mod h1:9NiDSp5zOcgEDl+j00MP/WkGVPOlPRLejGD8Ga6PJ7M=
 github.com/fjl/memsize v0.0.1 h1:+zhkb+dhUgx0/e+M8sF0QqiouvMQUiKR+QYvdxIOKcQ=
+github.com/fjl/memsize v0.0.1/go.mod h1:VvhXpOYNQvB+uIk2RvXzuaQtkQJzzIx6lSBe1xv7hi0=
 github.com/fsnotify/fsnotify v1.4.7/go.mod h1:jwhsz4b93w/PPRr/qN1Yymfu8t87LnFCMoQvtojpjFo=
 github.com/fsnotify/fsnotify v1.4.9/go.mod h1:znqG4EE+3YCdAaPaxE2ZRY/06pZUdp0tY4IgpuI1SZQ=
 github.com/fsnotify/fsnotify v1.5.4/go.mod h1:OVB6XrOHzAwXMpEM7uPOzcehqUV2UqJxmVXmkdnm1bU=
 github.com/fsnotify/fsnotify v1.6.0 h1:n+5WquG0fcWoWp6xPWfHdbskMCQaFnG6PfBrh1Ky4HY=
 github.com/fsnotify/fsnotify v1.6.0/go.mod h1:sl3t1tCWJFWoRz9R8WJCbQihKKwmorjAbSClcnxKAGw=
 github.com/gavv/httpexpect v2.0.0+incompatible/go.mod h1:x+9tiU1YnrOvnB725RkpoLv1M62hOWzwo5OXotisrKc=
 github.com/gballet/go-libpcsclite v0.0.0-20191108122812-4678299bea08 h1:f6D9Hr8xV8uYKlyuj8XIruxlh9WjVjdh1gIicAS7ays=
+github.com/gballet/go-libpcsclite v0.0.0-20191108122812-4678299bea08/go.mod h1:x7DCsMOv1taUwEWCzT4cmDeAkigA5/QCwUodaVOe8Ww=
 github.com/getsentry/sentry-go v0.12.0/go.mod h1:NSap0JBYWzHND8oMbyi0+XZhUalc1TBdRL1M71JZW2c=
 github.com/getsentry/sentry-go v0.18.0 h1:MtBW5H9QgdcJabtZcuJG80BMOwaBpkRDZkxRkNC1sN0=
 github.com/getsentry/sentry-go v0.18.0/go.mod h1:Kgon4Mby+FJ7ZWHFUAZgVaIa8sxHtnRJRLTXZr51aKQ=
@@ -133,6 +130,7 @@ github.com/gin-gonic/gin v1.4.0/go.mod h1:OW2EZn3DO8Ln9oIKOvM++LBO+5UPHJJDH72/q/
 github.com/go-check/check v0.0.0-20180628173108-788fd7840127/go.mod h1:9ES+weclKsC9YodN5RgxqK/VD9HM9JsCSh7rNhMZE98=
 github.com/go-errors/errors v1.0.1/go.mod h1:f4zRHt4oKfwPJE5k8C9vpYG+aDHdBFUsgrm6/TyX73Q=
 github.com/go-errors/errors v1.4.2 h1:J6MZopCL4uSllY1OfXM374weqZFFItUbrImctkmUxIA=
+github.com/go-errors/errors v1.4.2/go.mod h1:sIVyrIiJhuEF+Pj9Ebtd6P/rEYROXFi3BopGUQ5a5Og=
 github.com/go-martini/martini v0.0.0-20170121215854-22fa46961aab/go.mod h1:/P9AEU963A2AYjv4d1V5eVL1CQbEJq6aCNHDDjibzu8=
 github.com/go-ole/go-ole v1.2.6 h1:/Fpf6oFPoeFik9ty7siob0G6Ke8QvQEuVcuChpwXzpY=
 github.com/go-ole/go-ole v1.2.6/go.mod h1:pprOEPIfldk/42T2oK7lQ4v4JSDwmV0As9GaiUsvbm0=
@@ -152,7 +150,8 @@ github.com/gogo/protobuf v1.3.2/go.mod h1:P1XiOD3dCwIKUDQYPy72D8LYyHL2YPYrpS2s69
 github.com/gogo/status v1.1.0/go.mod h1:BFv9nrluPLmrS0EmGVvLaPNmRosr9KapBYd5/hpY1WM=
 github.com/golang-jwt/jwt v3.2.2+incompatible h1:IfV12K8xAKAnZqdXVzCZ+TOjboZ2keLg81eXfW3O+oY=
 github.com/golang-jwt/jwt v3.2.2+incompatible/go.mod h1:8pz2t5EyA70fFQQSrl6XZXzqecmYZeUEB8OUGHkxJ+I=
-github.com/golang-jwt/jwt/v4 v4.4.2 h1:rcc4lwaZgFMCZ5jxF9ABolDcIHdBytAFgqFPbSJQAYs=
+github.com/golang-jwt/jwt/v4 v4.5.0 h1:7cYmW1XlMY7h7ii7UhUyChSgS5wUJEnm9uZVTGqOWzg=
+github.com/golang-jwt/jwt/v4 v4.5.0/go.mod h1:m21LjoU+eqJr34lmDMbreY2eSTRJ1cv77w39/MY0Ch0=
 github.com/golang/glog v0.0.0-20160126235308-23def4e6c14b/go.mod h1:SBH7ygxi8pfUlaOkMMuAQtPIUF8ecWP5IEl/CR7VP2Q=
 github.com/golang/groupcache v0.0.0-20200121045136-8c9f03a8e57e/go.mod h1:cIg4eruTrX1D+g88fzRXU5OdNfaM+9IcxsU14FzY7Hc=
 github.com/golang/groupcache v0.0.0-20210331224755-41bb18bfe9da h1:oI5xCqsCo564l8iNU+DwB5epxmsaqB+rhGL0m5jtYqE=
@@ -162,7 +161,6 @@ github.com/golang/protobuf v1.2.0/go.mod h1:6lQm79b+lXiMfvg/cZm0SGofjICqVBUtrP5y
 github.com/golang/protobuf v1.3.1/go.mod h1:6lQm79b+lXiMfvg/cZm0SGofjICqVBUtrP5yJMmIC1U=
 github.com/golang/protobuf v1.3.2/go.mod h1:6lQm79b+lXiMfvg/cZm0SGofjICqVBUtrP5yJMmIC1U=
 github.com/golang/protobuf v1.3.3/go.mod h1:vzj43D7+SQXF/4pzW/hwtAqwc6iTitCiVSaWz5lYuqw=
-github.com/golang/protobuf v1.3.5/go.mod h1:6O5/vntMXwX2lRkT1hjjk0nAC1IDOTvTlVgjlRvqsdk=
 github.com/golang/protobuf v1.4.0-rc.1/go.mod h1:ceaxUfeHdC40wWswd/P6IGgMaK3YpKi5j83Wpe3EHw8=
 github.com/golang/protobuf v1.4.0-rc.1.0.20200221234624-67d41d38c208/go.mod h1:xKAWHe0F5eneWXFV3EuXVDTCmh+JuBKY0li0aMyXATA=
 github.com/golang/protobuf v1.4.0-rc.2/go.mod h1:LlEzMj4AhA7rCAGe4KMBDvJI+AwstrUpVNzEA03Pprs=
@@ -195,7 +193,8 @@ github.com/google/s2a-go v0.1.4 h1:1kZ/sQM3srePvKs3tXAvQzo66XfcReoqFpIpIccE7Oc=
 github.com/google/s2a-go v0.1.4/go.mod h1:Ej+mSEMGRnqRzjc7VtF+jdBwYG5fuJfiZ8ELkjEwM0A=
 github.com/google/subcommands v1.2.0/go.mod h1:ZjhPrFU+Olkh9WazFPsl27BQ4UPiG37m3yTrtFlrHVk=
 github.com/google/uuid v1.1.2/go.mod h1:TIyPZe4MgqvfeYDBFedMoGGpEw/LqOeaOT+nhxU+yHo=
-github.com/google/uuid v1.3.0 h1:t6JiXgmwXMjEs8VusXIJk2BXHsn+wx8BZdTaoZ5fu7I=
+github.com/google/uuid v1.3.1 h1:KjJaJ9iWZ3jOFZIf1Lqf4laDRCasjl0BCmnEGxkdLb4=
+github.com/google/uuid v1.3.1/go.mod h1:TIyPZe4MgqvfeYDBFedMoGGpEw/LqOeaOT+nhxU+yHo=
 github.com/googleapis/enterprise-certificate-proxy v0.2.5 h1:UR4rDjcgpgEnqpIEvkiqTYKBCKLNmlge2eVjoZfySzM=
 github.com/googleapis/enterprise-certificate-proxy v0.2.5/go.mod h1:RxW0N9901Cko1VOCW3SXCpWP+mlIEkk2tP7jnHy9a3w=
 github.com/googleapis/gax-go/v2 v2.12.0 h1:A+gCJKdRfqXkr+BIRGtZLibNXf0m1f9E4HG56etFpas=
@@ -208,15 +207,18 @@ github.com/gorilla/websocket v1.5.0 h1:PPwGk2jz7EePpoHN/+ClbZu8SPxiqlu12wZP/3sWm
 github.com/gorilla/websocket v1.5.0/go.mod h1:YR8l580nyteQvAITg2hZ9XVh4b55+EU/adAjf1fMHhE=
 github.com/grpc-ecosystem/grpc-gateway v1.16.0/go.mod h1:BDjrQk3hbvj6Nolgz8mAMFbcEtjT1g+wF4CSlocrBnw=
 github.com/hashicorp/go-bexpr v0.1.11 h1:6DqdA/KBjurGby9yTY0bmkathya0lfwF2SeuubCI7dY=
+github.com/hashicorp/go-bexpr v0.1.11/go.mod h1:f03lAo0duBlDIUMGCuad8oLcgejw4m7U+N8T+6Kz1AE=
 github.com/hashicorp/go-version v1.2.0/go.mod h1:fltr4n8CU8Ke44wwGCBoEymUuxUHl09ZGVZPK5anwXA=
 github.com/hashicorp/hcl v1.0.0/go.mod h1:E5yfLk+7swimpb2L/Alb/PJmXilQ/rhwaUYs4T20WEQ=
 github.com/holiman/billy v0.0.0-20230718173358-1c7e68d277a7 h1:3JQNjnMRil1yD0IfZKHF9GxxWKDJGj8I0IqOUol//sw=
+github.com/holiman/billy v0.0.0-20230718173358-1c7e68d277a7/go.mod h1:5GuXa7vkL8u9FkFuWdVvfR5ix8hRB7DbOAaYULamFpc=
 github.com/holiman/bloomfilter/v2 v2.0.3 h1:73e0e/V0tCydx14a0SCYS/EWCxgwLZ18CZcZKVu0fao=
 github.com/holiman/bloomfilter/v2 v2.0.3/go.mod h1:zpoh+gs7qcpqrHr3dB55AMiJwo0iURXE7ZOP9L9hSkA=
 github.com/holiman/uint256 v1.2.3 h1:K8UWO1HUJpRMXBxbmaY1Y8IAMZC/RsKB+ArEnnK4l5o=
 github.com/holiman/uint256 v1.2.3/go.mod h1:SC8Ryt4n+UBbPbIBKaG9zbbDlp4jOru9xFZmPzLUTxw=
 github.com/hpcloud/tail v1.0.0/go.mod h1:ab1qPbhIpdTxEkNHXyeSf5vhxWSCs/tWer42PpOxQnU=
-github.com/huin/goupnp v1.0.3 h1:N8No57ls+MnjlB+JPiCVSOyy/ot7MJTqlo7rn+NYSqQ=
+github.com/huin/goupnp v1.3.0 h1:UvLUlWDNpoUdYzb2TCn+MuTWtcjXKSza2n6CBdQ0xXc=
+github.com/huin/goupnp v1.3.0/go.mod h1:gnGPsThkYa7bFi/KWmEysQRf48l2dvR5bxr2OFckNX8=
 github.com/hydrogen18/memlistener v0.0.0-20200120041712-dcc25e7acd91/go.mod h1:qEIFzExnS6016fRpRfxrExeVn2gbClQA99gQhnIcdhE=
 github.com/ianlancetaylor/demangle v0.0.0-20200824232613-28f6c0f3b639/go.mod h1:aSSvb/t6k1mPoxDqO4vJh6VOCGPwU4O0C2/Eqndh1Sc=
 github.com/imkira/go-interpol v1.1.0/go.mod h1:z0h2/2T3XF8kyEPpRgJ3kmNv+C43p+I/CoI+jC3w2iA=
@@ -227,6 +229,7 @@ github.com/iris-contrib/jade v1.1.3/go.mod h1:H/geBymxJhShH5kecoiOCSssPX7QWYH7Ua
 github.com/iris-contrib/pongo2 v0.0.1/go.mod h1:Ssh+00+3GAZqSQb30AvBRNxBx7rf0GqwkjqxNd0u65g=
 github.com/iris-contrib/schema v0.0.1/go.mod h1:urYA3uvUNG1TIIjOSCzHr9/LmbQo8LrOcOqfqxa4hXw=
 github.com/jackpal/go-nat-pmp v1.0.2 h1:KzKSgb7qkJvOUTqYl9/Hg/me3pWgBmERKrTGD7BdWus=
+github.com/jackpal/go-nat-pmp v1.0.2/go.mod h1:QPH045xvCAeXUZOxsnwmrtiCoxIr9eob+4orBN1SBKc=
 github.com/json-iterator/go v1.1.6/go.mod h1:+SdeFBvtyEkXs7REEP0seUULqWtbJapLOCVDaaPEHmU=
 github.com/json-iterator/go v1.1.9/go.mod h1:KdQUCv79m/52Kvf8AW2vK1V8akMuk1QjK/uOdHXbAo4=
 github.com/jtolds/gls v4.20.0+incompatible/go.mod h1:QJZ7F/aHp+rZTRtaJ1ow/lLfFfVYBRgL+9YlvaHOwJU=
@@ -240,8 +243,6 @@ github.com/kisielk/errcheck v1.5.0/go.mod h1:pFxgyoBC7bSaBwPgfKdkLd5X25qrDl4LWUI
 github.com/kisielk/gotool v1.0.0/go.mod h1:XhKaO+MFFWcvkIS/tQcRk01m1F5IRFswLeQ+oQHNcck=
 github.com/klauspost/compress v1.8.2/go.mod h1:RyIbtBH6LamlWaDj8nUwkbUhJ87Yi3uG0guNDohfE1A=
 github.com/klauspost/compress v1.9.7/go.mod h1:RyIbtBH6LamlWaDj8nUwkbUhJ87Yi3uG0guNDohfE1A=
-github.com/klauspost/compress v1.15.15 h1:EF27CXIuDsYJ6mmvtBRlEuB2UVOqHG1tAXgZ7yIO+lw=
-github.com/klauspost/compress v1.15.15/go.mod h1:ZcK2JAFqKOpnBlxcLsJzYfrS9X1akm9fHZNnD9+Vo/4=
 github.com/klauspost/compress v1.16.7 h1:2mk3MPGNzKyxErAw8YaohYh69+pa4sIQSC0fPGCFR9I=
 github.com/klauspost/compress v1.16.7/go.mod h1:ntbaceVETuRiXiv4DpjP66DpAtAGkEQskQzEyD//IeE=
 github.com/klauspost/cpuid v1.2.1/go.mod h1:Pj4uuM528wm8OyEC2QMXAi2YiTZ96dNQPGgoMS4s3ek=
@@ -254,23 +255,25 @@ github.com/kr/text v0.1.0/go.mod h1:4Jbv+DJW3UT/LiOwJeYQe1efqtUx/iVham/4vfdArNI=
 github.com/kr/text v0.2.0 h1:5Nx0Ya0ZqY2ygV366QzturHI13Jq95ApcVaJBhpS+AY=
 github.com/kr/text v0.2.0/go.mod h1:eLer722TekiGuMkidMxC/pM04lWEeraHUUmBw8l2grE=
 github.com/kylelemons/godebug v1.1.0 h1:RPNrshWIDI6G2gRW9EHilWtl7Z6Sb1BR0xunSBf0SNc=
+github.com/kylelemons/godebug v1.1.0/go.mod h1:9/0rRGxNHcop5bhtWyNeEfOS8JIWk580+fNqagV/RAw=
 github.com/labstack/echo/v4 v4.5.0/go.mod h1:czIriw4a0C1dFun+ObrXp7ok03xON0N1awStJ6ArI7Y=
 github.com/labstack/gommon v0.3.0/go.mod h1:MULnywXg0yavhxWKc+lOruYdAhDwPK9wf0OL7NoOu+k=
 github.com/leanovate/gopter v0.2.9 h1:fQjYxZaynp97ozCzfOyOuAGOU4aU/z37zf/tOujFk7c=
+github.com/leanovate/gopter v0.2.9/go.mod h1:U2L/78B+KVFIx2VmW6onHJQzXtFb+p5y3y2Sh+Jxxv8=
 github.com/magiconair/properties v1.8.0/go.mod h1:PppfXfuXeibc/6YijjN8zIbojt8czPbwD3XqdrwzmxQ=
 github.com/mattn/go-colorable v0.1.2/go.mod h1:U0ppj6V5qS13XJ6of8GYAs25YV2eR4EVcfRqFIhoBtE=
 github.com/mattn/go-colorable v0.1.8/go.mod h1:u6P/XSegPjTcexA+o6vUJrdnUu04hMope9wVRipJSqc=
 github.com/mattn/go-colorable v0.1.11/go.mod h1:u5H1YNBxpqRaxsYJYSkiCWKzEfiAb1Gb520KVy5xxl4=
 github.com/mattn/go-colorable v0.1.13 h1:fFA4WZxdEF4tXPZVKMLwD8oUnCTTo08duU7wxecdEvA=
+github.com/mattn/go-colorable v0.1.13/go.mod h1:7S9/ev0klgBDR4GtXTXX8a3vIGJpMovkB8vQcUbaXHg=
 github.com/mattn/go-isatty v0.0.7/go.mod h1:Iq45c/XA43vh69/j3iqttzPXn0bhXyGjM0Hdxcsrc5s=
 github.com/mattn/go-isatty v0.0.8/go.mod h1:Iq45c/XA43vh69/j3iqttzPXn0bhXyGjM0Hdxcsrc5s=
 github.com/mattn/go-isatty v0.0.9/go.mod h1:YNRxwqDuOph6SZLI9vUUz6OYw3QyUt7WiY2yME+cCiQ=
 github.com/mattn/go-isatty v0.0.12/go.mod h1:cbi8OIDigv2wuxKPP5vlRcQ1OAZbq2CE4Kysco4FUpU=
 github.com/mattn/go-isatty v0.0.14/go.mod h1:7GGIvUiUoEMVVmxf/4nioHXj79iQHKdU27kJ6hsGG94=
-github.com/mattn/go-isatty v0.0.16 h1:bq3VjFmv/sOjHtdEhmkEV4x1AJtvUvOJ2PFAZ5+peKQ=
+github.com/mattn/go-isatty v0.0.19 h1:JITubQf0MOLdlGRuRq+jtsDlekdYPia9ZFsB8h/APPA=
+github.com/mattn/go-isatty v0.0.19/go.mod h1:W+V8PltTTMOvKvAeJH7IuucS94S2C6jfK/D7dTCTo3Y=
 github.com/mattn/go-runewidth v0.0.9/go.mod h1:H031xJmbD/WCDINGzjvQ9THkh0rPKHF+m2gUSrubnMI=
-github.com/mattn/go-runewidth v0.0.13 h1:lTGmDsbAYt5DmK6OnoV7EuIF1wEIFAcxld6ypU4OSgU=
-github.com/mattn/go-runewidth v0.0.13/go.mod h1:Jdepj2loyihRzMpdS35Xk/zdY8IAYHsh153qUoGf23w=
 github.com/mattn/go-runewidth v0.0.14 h1:+xnbZSEeDbOIg5/mE6JF0w6n9duR1l3/WmbinWVwUuU=
 github.com/mattn/go-runewidth v0.0.14/go.mod h1:Jdepj2loyihRzMpdS35Xk/zdY8IAYHsh153qUoGf23w=
 github.com/mattn/goveralls v0.0.2/go.mod h1:8d1ZMHsd7fW6IRPKQh46F2WRpyib5/X4FOpevwGNQEw=
@@ -281,7 +284,9 @@ github.com/microcosm-cc/bluemonday v1.0.2/go.mod h1:iVP4YcDBq+n/5fb23BhYFvIMq/le
 github.com/mitchellh/go-homedir v1.1.0/go.mod h1:SfyaCUpYCn1Vlf4IUYiD9fPX4A5wJrkLzIz1N1q0pr0=
 github.com/mitchellh/mapstructure v1.1.2/go.mod h1:FVVH3fgwuzCH5S8UJGiWEs2h04kUh9fWfEaFds41c1Y=
 github.com/mitchellh/mapstructure v1.5.0 h1:jeMsZIYE/09sWLaz43PL7Gy6RuMjD2eJVyuac5Z2hdY=
+github.com/mitchellh/mapstructure v1.5.0/go.mod h1:bFUtVrKA4DC2yAKiSyO/QUcy7e+RRV2QTWOzhPopBRo=
 github.com/mitchellh/pointerstructure v1.2.1 h1:ZhBBeX8tSlRpu/FFhXH4RC4OJzFlqsQhoHZAz4x7TIw=
+github.com/mitchellh/pointerstructure v1.2.1/go.mod h1:BRAsLI5zgXmw97Lf6s25bs8ohIXc3tViBH44KcwB2g4=
 github.com/mmcloughlin/addchain v0.4.0 h1:SobOdjm2xLj1KkXN5/n0xTIWyZA2+s99UCY1iPfkHRY=
 github.com/mmcloughlin/addchain v0.4.0/go.mod h1:A86O+tHqZLMNO4w6ZZ4FlVQEadcoqkyU72HC5wJ4RlU=
 github.com/mmcloughlin/profile v0.1.1/go.mod h1:IhHD7q1ooxgwTgjxQYkACGA77oFTDdFVejUS1/tS/qU=
@@ -309,8 +314,9 @@ github.com/onsi/ginkgo/v2 v2.1.3/go.mod h1:vw5CSIxN1JObi/U8gcbwft7ZxR2dgaR70JSE3
 github.com/onsi/gomega v1.7.1/go.mod h1:XdKZgCCFLUoM/7CFJVPcG8C1xQ1AJ0vpAezJrB7JYyY=
 github.com/onsi/gomega v1.10.1/go.mod h1:iN09h71vgCQne3DLsj+A5owkum+a2tYe+TOCB1ybHNo=
 github.com/onsi/gomega v1.17.0/go.mod h1:HnhC7FXeEQY45zxNK3PPoIUhzk/80Xly9PcubAlGdZY=
-github.com/onsi/gomega v1.19.0 h1:4ieX6qQjPP/BfC3mpsAtIGGlxTWPeA3Inl/7DtXw1tw=
 github.com/onsi/gomega v1.19.0/go.mod h1:LY+I3pBVzYsTBU1AnDwOSxaYi9WoWiqgwooUqq9yPro=
+github.com/onsi/gomega v1.28.0 h1:i2rg/p9n/UqIDAMFUJ6qIUUMcsqOuUHgbpbu235Vr1c=
+github.com/onsi/gomega v1.28.0/go.mod h1:A1H2JE76sI14WIP57LMKj7FVfCHx3g3BcZVjJG8bjX8=
 github.com/pelletier/go-toml v1.2.0/go.mod h1:5z9KED0ma1S8pY6P1sdut58dfprrGBbd/94hg7ilaic=
 github.com/pingcap/errors v0.11.4 h1:lFuQV/oaUMGcD2tqt+01ROSmJs75VG1ToEOkZIZ4nE4=
 github.com/pingcap/errors v0.11.4/go.mod h1:Oi8TUi2kEtXXLMJk9l1cGmz20kV3TaQ0usTwv5KuLY8=
@@ -320,39 +326,27 @@ github.com/pkg/errors v0.9.1 h1:FEBLx1zS214owpjy7qsBeixbURkuhQAwrK5UwLGTwt4=
 github.com/pkg/errors v0.9.1/go.mod h1:bwawxfHBFNV+L2hUp1rHADufV3IMtnDRdf1r5NINEl0=
 github.com/pmezard/go-difflib v1.0.0 h1:4DBwDE0NGyQoBHbLQYPwSUPoCMWR5BEzIk/f1lZbAQM=
 github.com/pmezard/go-difflib v1.0.0/go.mod h1:iKH77koFhYxTK1pcRnkKkqfTogsbg7gZNVY4sRDYZ/4=
-github.com/prometheus/client_golang v1.16.0 h1:yk/hx9hDbrGHovbci4BY+pRMfSuuat626eFsHb7tmT8=
-github.com/prometheus/client_golang v1.16.0/go.mod h1:Zsulrv/L9oM40tJ7T815tM89lFEugiJ9HzIqaAx4LKc=
 github.com/prometheus/client_golang v1.17.0 h1:rl2sfwZMtSthVU752MqfjQozy7blglC+1SOtjMAMh+Q=
 github.com/prometheus/client_golang v1.17.0/go.mod h1:VeL+gMmOAxkS2IqfCq0ZmHSL+LjWfWDUmp1mBz9JgUY=
 github.com/prometheus/client_model v0.0.0-20190812154241-14fe0d1b01d4/go.mod h1:xMI15A0UPsDsEKsMN9yxemIoYk6Tm2C1GtYGdfGttqA=
-github.com/prometheus/client_model v0.3.0 h1:UBgGFHqYdG/TPFD1B1ogZywDqEkwp3fBMvqdiQ7Xew4=
-github.com/prometheus/client_model v0.3.0/go.mod h1:LDGWKZIo7rky3hgvBe+caln+Dr3dPggB5dvjtD7w9+w=
 github.com/prometheus/client_model v0.4.1-0.20230718164431-9a2bf3000d16 h1:v7DLqVdK4VrYkVD5diGdl4sxJurKJEMnODWRJlxV9oM=
 github.com/prometheus/client_model v0.4.1-0.20230718164431-9a2bf3000d16/go.mod h1:oMQmHW1/JoDwqLtg57MGgP/Fb1CJEYF2imWWhWtMkYU=
-github.com/prometheus/common v0.42.0 h1:EKsfXEYo4JpWMHH5cg+KOUWeuJSov1Id8zGR8eeI1YM=
-github.com/prometheus/common v0.42.0/go.mod h1:xBwqVerjNdUDjgODMpudtOMwlOwf2SaTr1yjz4b7Zbc=
 github.com/prometheus/common v0.44.0 h1:+5BrQJwiBB9xsMygAB3TNvpQKOwlkc25LbISbrdOOfY=
 github.com/prometheus/common v0.44.0/go.mod h1:ofAIvZbQ1e/nugmZGz4/qCb9Ap1VoSTIO7x0VV9VvuY=
-github.com/prometheus/procfs v0.10.1 h1:kYK1Va/YMlutzCGazswoHKo//tZVlFpKYh+PymziUAg=
-github.com/prometheus/procfs v0.10.1/go.mod h1:nwNm2aOCAYw8uTR/9bWRREkZFxAUcWzPHWJq+XBB/FM=
 github.com/prometheus/procfs v0.11.1 h1:xRC8Iq1yyca5ypa9n1EZnWZkt7dwcoRPQwX/5gwaUuI=
 github.com/prometheus/procfs v0.11.1/go.mod h1:eesXgaPo1q7lBpVMoMy0ZOFTth9hBn4W/y0/p/ScXhY=
 github.com/rivo/uniseg v0.2.0/go.mod h1:J6wj4VEh+S6ZtnVlnTBMWIodfgj8LQOQFoIToxlJtxc=
-github.com/rivo/uniseg v0.3.4 h1:3Z3Eu6FGHZWSfNKJTOUiPatWwfc7DzJRU04jFUqJODw=
-github.com/rivo/uniseg v0.3.4/go.mod h1:FN3SvrM+Zdj16jyLfmOkMNblXMcoc8DfTHruCPUcx88=
 github.com/rivo/uniseg v0.4.3 h1:utMvzDsuh3suAEnhH0RdHmoPbU648o6CvXxTx4SBMOw=
 github.com/rivo/uniseg v0.4.3/go.mod h1:FN3SvrM+Zdj16jyLfmOkMNblXMcoc8DfTHruCPUcx88=
 github.com/rogpeppe/fastuuid v1.2.0/go.mod h1:jVj6XXZzXRy/MSR5jhDC/2q6DgLz+nrA6LYCDYWNEvQ=
 github.com/rogpeppe/go-internal v1.6.1/go.mod h1:xXDCJY+GAPziupqXw64V24skbSoqbTEfhy4qGm1nDQc=
 github.com/rogpeppe/go-internal v1.8.1/go.mod h1:JeRgkft04UBgHMgCIwADu4Pn6Mtm5d4nPKWu0nJ5d+o=
-github.com/rogpeppe/go-internal v1.9.0 h1:73kH8U+JUqXU8lRuOHeVHaa/SZPifC7BkcraZVejAe8=
 github.com/rogpeppe/go-internal v1.9.0/go.mod h1:WtVeX8xhTBvf0smdhujwtBcq4Qrzq/fJaraNFVN+nFs=
 github.com/rogpeppe/go-internal v1.10.0 h1:TMyTOH3F/DB16zRVcYyreMH6GnZZrwQVAoYjRBZyWFQ=
 github.com/rogpeppe/go-internal v1.10.0/go.mod h1:UQnix2H7Ngw/k4C5ijL5+65zddjncjaFoBhdsK/akog=
 github.com/rs/cors v1.9.0 h1:l9HGsTsHJcvW14Nk7J9KFz8bzeAWXn3CG6bgt7LsrAE=
 github.com/rs/cors v1.9.0/go.mod h1:XyqrcTp5zjWr1wsJ8PIRZssZ8b/WMcMf71DJnit4EMU=
 github.com/russross/blackfriday v1.5.2/go.mod h1:JO/DiYxRf+HjHt06OyowR9PTA263kcR/rfWxYHBV53g=
-github.com/russross/blackfriday/v2 v2.0.1/go.mod h1:+Rmxgy9KzJVeS9/2gXHxylqXiyQDYRxCVz55jmeOWTM=
 github.com/russross/blackfriday/v2 v2.1.0 h1:JIOH55/0cWyOuilr9/qlrm0BSXldqnqwMsf35Ld67mk=
 github.com/russross/blackfriday/v2 v2.1.0/go.mod h1:+Rmxgy9KzJVeS9/2gXHxylqXiyQDYRxCVz55jmeOWTM=
 github.com/ryanuber/columnize v2.1.0+incompatible/go.mod h1:sm1tb6uqfes/u+d4ooFouqFdy9/2g9QGwK3SQygK0Ts=
@@ -370,6 +364,7 @@ github.com/spf13/jwalterweatherman v1.0.0/go.mod h1:cQK4TGJAtQXfYWX+Ddv3mKDzgVb6
 github.com/spf13/pflag v1.0.3/go.mod h1:DYY7MBk1bdzusC3SYhjObp+wFpr4gzcvqqNjLnInEg4=
 github.com/spf13/viper v1.3.2/go.mod h1:ZiWeW+zYFKm7srdB9IoDzzZXaJaI5eL9QjNiN/DMA2s=
 github.com/status-im/keycard-go v0.2.0 h1:QDLFswOQu1r5jsycloeQh3bVU8n/NatHHaZobtDnDzA=
+github.com/status-im/keycard-go v0.2.0/go.mod h1:wlp8ZLbsmrF6g6WjugPAx+IzoLrkdf9+mHxBEeo3Hbg=
 github.com/stretchr/objx v0.1.0/go.mod h1:HFkY916IF+rwdDfMAkV7OtwuqBVzrE8GR6GFx+wExME=
 github.com/stretchr/objx v0.4.0/go.mod h1:YvHI0jy2hoMjB+UWwv71VJQ9isScKT/TqJzVSSt89Yw=
 github.com/stretchr/objx v0.5.0/go.mod h1:Yh+to48EsGEfYuaHDzXPcE3xhTkx73EhmCGUpEOglKo=
@@ -382,28 +377,22 @@ github.com/stretchr/testify v1.7.1/go.mod h1:6Fq8oRcR53rry900zMqJjRRixrwX3KX962/
 github.com/stretchr/testify v1.7.2/go.mod h1:R6va5+xMeoiuVRoj+gSkQ7d3FALtqAAGI1FQKckRals=
 github.com/stretchr/testify v1.8.0/go.mod h1:yNjHg4UonilssWZ8iaSj1OCr/vHnekPRkoO+kdMU+MU=
 github.com/stretchr/testify v1.8.1/go.mod h1:w2LPCIKwWwSfY2zedu0+kehJoqGctiVI29o6fzry7u4=
-github.com/stretchr/testify v1.8.2 h1:+h33VjcLVPDHtOdpUCuF+7gSuG3yGIftsP1YvFihtJ8=
+github.com/stretchr/testify v1.8.4 h1:CcVxjf3Q8PM0mHUKJCdn+eZZtm5yQwehR5yeSVQQcUk=
+github.com/stretchr/testify v1.8.4/go.mod h1:sz/lmYIOXD/1dqDmKjjqLyZ2RngseejIcXlSw2iwfAo=
 github.com/supranational/blst v0.3.11 h1:LyU6FolezeWAhvQk0k6O/d49jqgO52MSDDfYgbeoEm4=
 github.com/supranational/blst v0.3.11/go.mod h1:jZJtfjgudtNl4en1tzwPIV3KjUnQUvG3/j+w+fVonLw=
 github.com/syndtr/goleveldb v1.0.1-0.20220614013038-64ee5596c38a h1:1ur3QoCqvE5fl+nylMaIr9PVV1w343YRDtsy+Rwu7XI=
 github.com/syndtr/goleveldb v1.0.1-0.20220614013038-64ee5596c38a/go.mod h1:RRCYJbIwD5jmqPI9XoAFR0OcDxqUctll6zUj/+B4S48=
-github.com/tklauser/go-sysconf v0.3.10 h1:IJ1AZGZRWbY8T5Vfk04D9WOA5WSejdflXxP03OUqALw=
-github.com/tklauser/go-sysconf v0.3.10/go.mod h1:C8XykCvCb+Gn0oNCWPIlcb0RuglQTYaQ2hGm7jmxEFk=
 github.com/tklauser/go-sysconf v0.3.12 h1:0QaGUFOdQaIVdPgfITYzaTegZvdCjmYO52cSFAEVmqU=
 github.com/tklauser/go-sysconf v0.3.12/go.mod h1:Ho14jnntGE1fpdOqQEEaiKRpvIavV0hSfmBq8nJbHYI=
-github.com/tklauser/numcpus v0.4.0/go.mod h1:1+UI3pD8NW14VMwdgJNJ1ESk2UnwhAnz5hMwiKKqXCQ=
-github.com/tklauser/numcpus v0.5.0 h1:ooe7gN0fg6myJ0EKoTAf5hebTZrH52px3New/D9iJ+A=
-github.com/tklauser/numcpus v0.5.0/go.mod h1:OGzpTxpcIMNGYQdit2BYL1pvk/dSOaJWjKoflh+RQjo=
 github.com/tklauser/numcpus v0.6.1 h1:ng9scYS7az0Bk4OZLvrNXNSAO2Pxr1XXRAPyjhIx+Fk=
 github.com/tklauser/numcpus v0.6.1/go.mod h1:1XfjsgE2zo8GVw7POkMbHENHzVg3GzmoZ9fESEdAacY=
 github.com/tyler-smith/go-bip39 v1.1.0 h1:5eUemwrMargf3BSLRRCalXT93Ns6pQJIjYQN2nyfOP8=
+github.com/tyler-smith/go-bip39 v1.1.0/go.mod h1:gUYDtqQw1JS3ZJ8UWVcGTGqqr6YIN3CWg+kkNaLt55U=
 github.com/ugorji/go v1.1.4/go.mod h1:uQMGLiO92mf5W77hV/PUCpI3pbzQx3CRekS0kk+RGrc=
 github.com/ugorji/go v1.1.7/go.mod h1:kZn38zHttfInRq0xu/PH0az30d+z6vm202qpg1oXVMw=
 github.com/ugorji/go/codec v0.0.0-20181204163529-d75b2dcb6bc8/go.mod h1:VFNgLljTbGfSG7qAOspJ7OScBnGdDN/yBr0sguwnwf0=
 github.com/ugorji/go/codec v1.1.7/go.mod h1:Ax+UKWsSmolVDwsd+7N3ZtXu+yMGCf907BLYF3GoBXY=
-github.com/urfave/cli v1.22.9 h1:cv3/KhXGBGjEXLC4bH0sLuJ9BewaAbpk5oyMOveu4pw=
-github.com/urfave/cli v1.22.9/go.mod h1:Gos4lmkARVdJ6EkW0WaNv/tZAAMe9V7XWyB60NtXRu0=
-github.com/urfave/cli/v2 v2.24.1 h1:/QYYr7g0EhwXEML8jO+8OYt5trPnLHS0p3mrgExJ5NU=
 github.com/urfave/cli/v2 v2.25.7 h1:VAzn5oq403l5pHjc4OhD54+XGO9cdKVL/7lDjF+iKUs=
 github.com/urfave/cli/v2 v2.25.7/go.mod h1:8qnjx1vcq5s2/wpsqoZFndg2CE5tNFyrTvS6SinrnYQ=
 github.com/urfave/negroni v1.0.0/go.mod h1:Meg73S6kFm/4PpbYdq35yYWoCZ9mS/YSx+lKnmiohz4=
@@ -443,8 +432,6 @@ golang.org/x/crypto v0.0.0-20220314234659-1baeb1ce4c0b/go.mod h1:IxCIyHEi3zRg3s0
 golang.org/x/crypto v0.14.0 h1:wBqGXzWJW6m1XrIKlAH0Hs1JJ7+9KBwnIO8v66Q9cHc=
 golang.org/x/crypto v0.14.0/go.mod h1:MVFd36DqK4CsrnJYDkBA3VC4m2GkXAM0PvzMCn4JQf4=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
-golang.org/x/exp v0.0.0-20230515195305-f3d0a9c9a5cc h1:mCRnTeVUjcrhlRmO0VK8a6k6Rrf6TF9htwo2pJVSjIU=
-golang.org/x/exp v0.0.0-20230515195305-f3d0a9c9a5cc/go.mod h1:V1LtkGg67GoY2N1AnLN78QLrzxkLyJw7RJb1gzOOz9w=
 golang.org/x/exp v0.0.0-20230905200255-921286631fa9 h1:GoHiUyI/Tp2nVkLI2mCxVkOjsbSXD66ic0XW0js0R9g=
 golang.org/x/exp v0.0.0-20230905200255-921286631fa9/go.mod h1:S2oDrQGGwySpoQPVqRShND87VCbxmc6bL1Yd2oYrm6k=
 golang.org/x/lint v0.0.0-20181026193005-c67002cb31c3/go.mod h1:UVdnD1Gm6xHRNCYTkRU2/jEulfH38KcIWyp/GAMgvoE=
@@ -530,14 +517,12 @@ golang.org/x/sys v0.0.0-20210630005230-0f9fa26af87c/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20210927094055-39ccf1dd6fa6/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20211007075335-d3039528d8ac/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20211216021012-1d35b9e2eb4e/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/sys v0.0.0-20220128215802-99c3d69c2c27/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220209214540-3681064d5158/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/sys v0.0.0-20220405052023-b1e9470b6e64/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220412211240-33da011f77ad/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/sys v0.0.0-20220503163025-988cb79eb6c6/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220520151302-bc2c85ada10a/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220722155257-8c9f86f7a55f/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220908164124-27713097b956/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.5.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.8.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.11.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.13.0 h1:Af8nKPmuFypiUBjVoU9V20FiaFXOcuZI21p0ycVYYGE=
@@ -555,6 +540,7 @@ golang.org/x/text v0.13.0 h1:ablQoSUd0tRdKxZewP80B+BaqeKJuVhuRxj/dkrun3k=
 golang.org/x/text v0.13.0/go.mod h1:TvPlkZtksWOMsz7fbANvkp4WM8x/WCo/om8BMLbz+aE=
 golang.org/x/time v0.0.0-20201208040808-7e3f01d25324/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.3.0 h1:rg5rLMjNzMS1RkNLzCG38eapWhnYLFYXDXj2gOlr8j4=
+golang.org/x/time v0.3.0/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/tools v0.0.0-20180917221912-90fa682c2a6e/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20181221001348-537d06c36207/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20190114222345-bf090417da8b/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
@@ -605,8 +591,8 @@ google.golang.org/grpc v1.33.2/go.mod h1:JMHMWHQWaTccqQQlmk3MJZS+GWXOdAesneDmEnv
 google.golang.org/grpc v1.36.0/go.mod h1:qjiiYl8FncCW8feJPdyg3v6XW24KsRHe+dy9BAGRRjU=
 google.golang.org/grpc v1.38.0/go.mod h1:NREThFqKR1f3iQ6oBuvc5LadQuXVGo9rkm5ZGrQdJfM=
 google.golang.org/grpc v1.45.0/go.mod h1:lN7owxKUQEqMfSyQikvvk5tf/6zMPsrK+ONuO11+0rQ=
-google.golang.org/grpc v1.56.2 h1:fVRFRnXvU+x6C4IlHZewvJOVHoOv1TUuQyoRsYnB4bI=
-google.golang.org/grpc v1.56.2/go.mod h1:I9bI3vqKfayGqPUAwGdOSu7kt6oIJLixfffKrpXqQ9s=
+google.golang.org/grpc v1.56.3 h1:8I4C0Yq1EjstUzUJzpcRVbuYA2mODtEmpWiQoN/b2nc=
+google.golang.org/grpc v1.56.3/go.mod h1:I9bI3vqKfayGqPUAwGdOSu7kt6oIJLixfffKrpXqQ9s=
 google.golang.org/protobuf v0.0.0-20200109180630-ec00e32a8dfd/go.mod h1:DFci5gLYBciE7Vtevhsrf46CRTquxDuWsQurQQe4oz8=
 google.golang.org/protobuf v0.0.0-20200221191635-4d8936d0db64/go.mod h1:kwYJMbMJ01Woi6D6+Kah6886xMZcty6N08ah7+eCXa0=
 google.golang.org/protobuf v0.0.0-20200228230310-ab0ca4ff8a60/go.mod h1:cfTl7dwQJ+fmap5saPgwCLgHXTUD7jkjRqWcaiX5VyM=
@@ -624,15 +610,15 @@ gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405/go.mod h1:Co6ibVJAznAaIkqp8
 gopkg.in/check.v1 v1.0.0-20180628173108-788fd7840127/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
 gopkg.in/check.v1 v1.0.0-20190902080502-41f04d3bba15/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
 gopkg.in/check.v1 v1.0.0-20201130134442-10cb98267c6c h1:Hei/4ADfdWqJk1ZMxUNpqntNwaWcugrBjAiHlqqRiVk=
+gopkg.in/check.v1 v1.0.0-20201130134442-10cb98267c6c/go.mod h1:JHkPIbrfpd72SG/EVd6muEfDQjcINNoR0C8j2r3qZ4Q=
 gopkg.in/errgo.v2 v2.1.0/go.mod h1:hNsd1EY+bozCKY1Ytp96fpM3vjJbqLJn88ws8XvfDNI=
 gopkg.in/fsnotify.v1 v1.4.7/go.mod h1:Tz8NjZHkW78fSQdbUxIjBTcgA1z1m8ZHf0WmKUhAMys=
 gopkg.in/go-playground/assert.v1 v1.2.1/go.mod h1:9RXL0bg/zibRAgZUYszZSwO/z8Y/a8bDuhia5mkpMnE=
 gopkg.in/go-playground/validator.v8 v8.18.2/go.mod h1:RX2a/7Ha8BgOhfk7j780h4/u/RRjR0eouCJSH80/M2Y=
 gopkg.in/ini.v1 v1.51.1/go.mod h1:pNLf8WUiyNEtQjuu5G5vTm06TEv9tsIgeAvK8hOrP4k=
 gopkg.in/mgo.v2 v2.0.0-20180705113604-9856a29383ce/go.mod h1:yeKp02qBN3iKW1OzL3MGk2IdtZzaj7SFntXj72NppTA=
 gopkg.in/natefinch/lumberjack.v2 v2.0.0 h1:1Lc07Kr7qY4U2YPouBjpCLxpiyxIVoxqXgkXLknAOE8=
-gopkg.in/natefinch/npipe.v2 v2.0.0-20160621034901-c1b8fa8bdcce h1:+JknDZhAj8YMt7GC73Ei8pv4MzjDUNPHgQWJdtMAaDU=
-gopkg.in/natefinch/npipe.v2 v2.0.0-20160621034901-c1b8fa8bdcce/go.mod h1:5AcXVHNjg+BDxry382+8OKon8SEWiKktQR07RKPsv1c=
+gopkg.in/natefinch/lumberjack.v2 v2.0.0/go.mod h1:l0ndWWf7gzL7RNwBG7wST/UCcT4T24xpD6X8LsfU/+k=
 gopkg.in/tomb.v1 v1.0.0-20141024135613-dd632973f1e7 h1:uRGJdciOHaEIrze2W8Q3AKkepLTh2hOroT7a+7czfdQ=
 gopkg.in/tomb.v1 v1.0.0-20141024135613-dd632973f1e7/go.mod h1:dt/ZhP58zS4L8KSrWDmTeBkI65Dw0HsyUHuEVlX15mw=
 gopkg.in/yaml.v2 v2.2.2/go.mod h1:hI93XBmqTisBFMUTm0b8Fm+jr3Dg1NNxqwp+5A1VGuI=
```

### proxyd/go.mod
```diff
@@ -6,7 +6,7 @@ require (
 	github.com/BurntSushi/toml v1.3.2
 	github.com/alicebob/miniredis v2.5.0+incompatible
 	github.com/emirpasic/gods v1.18.1
-	github.com/ethereum/go-ethereum v1.13.4
+	github.com/ethereum/go-ethereum v1.13.5
 	github.com/go-redsync/redsync/v4 v4.10.0
 	github.com/golang/snappy v0.0.5-0.20220116011046-fa5810519dcb
 	github.com/gorilla/mux v1.8.0
```

### proxyd/go.sum
```diff
@@ -60,8 +60,8 @@ github.com/emirpasic/gods v1.18.1 h1:FXtiHYKDGKCW2KzwZKx0iC0PQmdlorYgdFG9jPXJ1Bc
 github.com/emirpasic/gods v1.18.1/go.mod h1:8tpGGwCnJ5H4r6BWwaV6OrWmMoPhUl5jm/FMNAnJvWQ=
 github.com/ethereum/c-kzg-4844 v0.4.0 h1:3MS1s4JtA868KpJxroZoepdV0ZKBp3u/O5HcZ7R3nlY=
 github.com/ethereum/c-kzg-4844 v0.4.0/go.mod h1:VewdlzQmpT5QSrVhbBuGoCdFJkpaJlO1aQputP83wc0=
-github.com/ethereum/go-ethereum v1.13.4 h1:25HJnaWVg3q1O7Z62LaaI6S9wVq8QCw3K88g8wEzrcM=
-github.com/ethereum/go-ethereum v1.13.4/go.mod h1:I0U5VewuuTzvBtVzKo7b3hJzDhXOUtn9mJW7SsIPB0Q=
+github.com/ethereum/go-ethereum v1.13.5 h1:U6TCRciCqZRe4FPXmy1sMGxTfuk8P7u2UoinF3VbaFk=
+github.com/ethereum/go-ethereum v1.13.5/go.mod h1:yMTu38GSuyxaYzQMViqNmQ1s3cE84abZexQmTgenWk0=
 github.com/fsnotify/fsnotify v1.4.7/go.mod h1:jwhsz4b93w/PPRr/qN1Yymfu8t87LnFCMoQvtojpjFo=
 github.com/fsnotify/fsnotify v1.4.9/go.mod h1:znqG4EE+3YCdAaPaxE2ZRY/06pZUdp0tY4IgpuI1SZQ=
 github.com/fsnotify/fsnotify v1.6.0 h1:n+5WquG0fcWoWp6xPWfHdbskMCQaFnG6PfBrh1Ky4HY=
```
