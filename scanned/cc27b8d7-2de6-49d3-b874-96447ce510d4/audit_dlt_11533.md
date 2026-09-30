# [?] fix: v1 mempool data race (#4380)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2025-03-06
Source: https://github.com/celestiaorg/celestia-app/commit/a3917ec78dd52681378ab391dba8bdee73a6954d
Type: security-commit

## Details
fix: v1 mempool data race (#4380)

Closes https://github.com/celestiaorg/celestia-app/issues/4379 by
upgrading to
https://github.com/celestiaorg/celestia-core/releases/tag/v1.49.1-tm-v0.34.35
which includes https://github.com/celestiaorg/celestia-core/pull/1655

## Patch
### go.mod
```diff
@@ -228,13 +228,13 @@ require (
 	go.opentelemetry.io/otel/trace v1.32.0 // indirect
 	go.uber.org/multierr v1.11.0 // indirect
 	go.uber.org/zap v1.27.0 // indirect
-	golang.org/x/crypto v0.32.0 // indirect
+	golang.org/x/crypto v0.35.0 // indirect
 	golang.org/x/net v0.34.0 // indirect
 	golang.org/x/oauth2 v0.24.0 // indirect
-	golang.org/x/sync v0.10.0 // indirect
-	golang.org/x/sys v0.29.0 // indirect
-	golang.org/x/term v0.28.0 // indirect
-	golang.org/x/text v0.21.0 // indirect
+	golang.org/x/sync v0.11.0 // indirect
+	golang.org/x/sys v0.30.0 // indirect
+	golang.org/x/term v0.29.0 // indirect
+	golang.org/x/text v0.22.0 // indirect
 	golang.org/x/time v0.9.0 // indirect
 	google.golang.org/api v0.169.0 // indirect
 	google.golang.org/genproto v0.0.0-20240227224415-6ceb2ff114de // indirect
@@ -260,5 +260,5 @@ replace (
 	github.com/cosmos/ibc-go/v6 => github.com/celestiaorg/ibc-go/v6 v6.2.3
 	github.com/gogo/protobuf => github.com/regen-network/protobuf v1.3.3-alpha.regen.1
 	github.com/syndtr/goleveldb => github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7
-	github.com/tendermint/tendermint => github.com/celestiaorg/celestia-core v1.47.0-tm-v0.34.35
+	github.com/tendermint/tendermint => github.com/celestiaorg/celestia-core v1.49.1-tm-v0.34.35
 )
```

### go.sum
```diff
@@ -318,8 +318,8 @@ github.com/celestiaorg/bittwister v0.0.0-20231213180407-65cdbaf5b8c7 h1:nxplQi8w
 github.com/celestiaorg/bittwister v0.0.0-20231213180407-65cdbaf5b8c7/go.mod h1:1EF5MfOxVf0WC51Gb7pJ6bcZxnXKNAf9pqWtjgPBAYc=
 github.com/celestiaorg/blobstream-contracts/v3 v3.1.0 h1:h1Y4V3EMQ2mFmNtWt2sIhZIuyASInj1a9ExI8xOsTOw=
 github.com/celestiaorg/blobstream-contracts/v3 v3.1.0/go.mod h1:x4DKyfKOSv1ZJM9NwV+Pw01kH2CD7N5zTFclXIVJ6GQ=
-github.com/celestiaorg/celestia-core v1.47.0-tm-v0.34.35 h1:K0kSVRlKfsPwfiA4o8GNUNPfZ+wF1MnYajom4CzJxpQ=
-github.com/celestiaorg/celestia-core v1.47.0-tm-v0.34.35/go.mod h1:FSd32MUffdVUYIXW+m/1v5pHptRQF2RJC88fwsgrKG8=
+github.com/celestiaorg/celestia-core v1.49.1-tm-v0.34.35 h1:Fgm7Wj+378S0ktzpWiuIpjJTTfQYk3CNXKwvjHYLHeg=
+github.com/celestiaorg/celestia-core v1.49.1-tm-v0.34.35/go.mod h1:SI38xqZZ4ccoAxszUJqsJ/a5rOkzQRijzHQQlLKkyUc=
 github.com/celestiaorg/cosmos-sdk v1.27.0-sdk-v0.46.16 h1:qxWiGrDEcg4FzVTpIXU/v3wjP7q1Lz4AMhSBBRABInU=
 github.com/celestiaorg/cosmos-sdk v1.27.0-sdk-v0.46.16/go.mod h1:W30mNt3+2l516HVR8Gt9+Gf4qOrWC9/x18MTEx2GljE=
 github.com/celestiaorg/go-square v1.1.1 h1:Cy3p8WVspVcyOqHM8BWFuuYPwMitO1pYGe+ImILFZRA=
@@ -1425,8 +1425,8 @@ golang.org/x/crypto v0.0.0-20201221181555-eec23a3978ad/go.mod h1:jdWPYTVW3xRLrWP
 golang.org/x/crypto v0.0.0-20210322153248-0c34fe9e7dc2/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
 golang.org/x/crypto v0.0.0-20210711020723-a769d52b0f97/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
 golang.org/x/crypto v0.0.0-20210921155107-089bfa567519/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
-golang.org/x/crypto v0.32.0 h1:euUpcYgM8WcP71gNpTqQCn6rC2t6ULUPiOzfWaXVVfc=
-golang.org/x/crypto v0.32.0/go.mod h1:ZnnJkOaASj8g0AjIduWNlq2NRxL0PlBrbKVyZ6V/Ugc=
+golang.org/x/crypto v0.35.0 h1:b15kiHdrGCHrP6LvwaQ3c03kgNhhiMgvlhxHQhmg2Xs=
+golang.org/x/crypto v0.35.0/go.mod h1:dy7dXNW32cAb/6/PRuTNsix8T+vJAqvuIy5Bli/x0YQ=
 golang.org/x/exp v0.0.0-20180321215751-8460e604b9de/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20180807140117-3d87b88a115f/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
@@ -1577,8 +1577,8 @@ golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.0.0-20220601150217-0de741cfad7f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20220722155255-886fb9371eb4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20220929204114-8fcdb60fdcc0/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
-golang.org/x/sync v0.10.0 h1:3NQrjDixjgGwUOCaF8w2+VYHv0Ve/vGYSbdkTa98gmQ=
-golang.org/x/sync v0.10.0/go.mod h1:Czt+wKu1gCyEFDUtn0jG5QVvpJ6rzVqr5aXyt9drQfk=
+golang.org/x/sync v0.11.0 h1:GGz8+XQP4FvTTrjZPzNKTMFtSXH80RAzG+5ghFPgK9w=
+golang.org/x/sync v0.11.0/go.mod h1:Czt+wKu1gCyEFDUtn0jG5QVvpJ6rzVqr5aXyt9drQfk=
 golang.org/x/sys v0.0.0-20180823144017-11551d06cbcc/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180830151530-49385e6e1522/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180905080454-ebe1bf3edb33/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -1689,14 +1689,14 @@ golang.org/x/sys v0.11.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.12.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.14.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
 golang.org/x/sys v0.21.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
-golang.org/x/sys v0.29.0 h1:TPYlXGxvx1MGTn2GiZDhnjPA9wZzZeGKHHmKhHYvgaU=
-golang.org/x/sys v0.29.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
+golang.org/x/sys v0.30.0 h1:QjkSwP/36a20jFYWkSue1YwXzLmsV5Gfq7Eiy72C1uc=
+golang.org/x/sys v0.30.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
 golang.org/x/term v0.0.0-20201117132131-f5c789dd3221/go.mod h1:Nr5EML6q2oocZ2LXRh80K7BxOlk5/8JxuGnuhpl+muw=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/term v0.1.0/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
-golang.org/x/term v0.28.0 h1:/Ts8HFuMR2E6IP/jlo7QVLZHggjKQbhu/7H0LJFr3Gg=
-golang.org/x/term v0.28.0/go.mod h1:Sw/lC2IAUZ92udQNf3WodGtn4k/XoLyZoh8v/8uiwek=
+golang.org/x/term v0.29.0 h1:L6pJp37ocefwRRtYPKSWOWzOtWSxVajvz2ldH/xi3iU=
+golang.org/x/term v0.29.0/go.mod h1:6bl4lRlvVuDgSf3179VpIxBF0o10JUpXWOnI7nErv7s=
 golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.1-0.20180807135948-17ff2d5776d2/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
@@ -1707,8 +1707,8 @@ golang.org/x/text v0.3.5/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
 golang.org/x/text v0.4.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
-golang.org/x/text v0.21.0 h1:zyQAAkrwaneQ066sspRyJaG9VNi/YJ1NfzcGB3hZ/qo=
-golang.org/x/text v0.21.0/go.mod h1:4IBbMaMmOPCJ8SecivzSH54+73PCFmPWxNTLm+vZkEQ=
+golang.org/x/text v0.22.0 h1:bofq7m3/HAFvbF51jz3Q9wLg3jkvSPuiZu/pD1XwgtM=
+golang.org/x/text v0.22.0/go.mod h1:YRoo4H8PVmsu+E3Ou7cqLVH8oXWIHVoX0jqUWALQhfY=
 golang.org/x/time v0.0.0-20180412165947-fbb02b2291d2/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20181108054448-85acf8d2951c/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20190308202827-9d24e82272b4/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
```

### test/interchain/go.mod
```diff
@@ -74,10 +74,10 @@ require (
 	github.com/gogo/gateway v1.1.0 // indirect
 	github.com/gogo/protobuf v1.3.3 // indirect
 	github.com/golang/glog v1.2.4 // indirect
-	github.com/golang/groupcache v0.0.0-20210331224755-41bb18bfe9da // indirect
+	github.com/golang/groupcache v0.0.0-20241129210726-2c02b8208cf8 // indirect
 	github.com/golang/protobuf v1.5.4 // indirect
 	github.com/golang/snappy v0.0.5-0.20220116011046-fa5810519dcb // indirect
-	github.com/google/btree v1.1.2 // indirect
+	github.com/google/btree v1.1.3 // indirect
 	github.com/google/pprof v0.0.0-20240827171923-fa2c70bbbfe5 // indirect
 	github.com/google/s2a-go v0.1.7 // indirect
 	github.com/google/uuid v1.6.0 // indirect
@@ -107,7 +107,7 @@ require (
 	github.com/jmespath/go-jmespath v0.4.0 // indirect
 	github.com/jmhodges/levigo v1.0.0 // indirect
 	github.com/kballard/go-shellquote v0.0.0-20180428030007-95032a82bc51 // indirect
-	github.com/klauspost/compress v1.17.9 // indirect
+	github.com/klauspost/compress v1.17.11 // indirect
 	github.com/klauspost/cpuid/v2 v2.2.6 // indirect
 	github.com/libp2p/go-buffer-pool v0.1.0 // indirect
 	github.com/libp2p/go-libp2p v0.27.8 // indirect
@@ -139,9 +139,9 @@ require (
 	github.com/pierrec/xxHash v0.1.5 // indirect
 	github.com/pkg/errors v0.9.1 // indirect
 	github.com/pmezard/go-difflib v1.0.1-0.20181226105442-5d4384ee4fb2 // indirect
-	github.com/prometheus/client_golang v1.20.3 // indirect
+	github.com/prometheus/client_golang v1.20.5 // indirect
 	github.com/prometheus/client_model v0.6.1 // indirect
-	github.com/prometheus/common v0.55.0 // indirect
+	github.com/prometheus/common v0.62.0 // indirect
 	github.com/prometheus/procfs v0.15.1 // indirect
 	github.com/rakyll/statik v0.1.7 // indirect
 	github.com/rcrowley/go-metrics v0.0.0-20201227073835-cf1acfcdf475 // indirect
@@ -170,7 +170,7 @@ require (
 	github.com/vedhavyas/go-subkey v1.0.3 // indirect
 	github.com/zondax/hid v0.9.2 // indirect
 	github.com/zondax/ledger-go v0.14.3 // indirect
-	go.etcd.io/bbolt v1.3.6 // indirect
+	go.etcd.io/bbolt v1.3.11 // indirect
 	go.opencensus.io v0.24.0 // indirect
 	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.47.0 // indirect
 	go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp v0.49.0 // indirect
@@ -179,23 +179,23 @@ require (
 	go.opentelemetry.io/otel/trace v1.30.0 // indirect
 	go.uber.org/atomic v1.11.0 // indirect
 	go.uber.org/multierr v1.11.0 // indirect
-	golang.org/x/crypto v0.31.0 // indirect
-	golang.org/x/exp v0.0.0-20240904232852-e7e105dedf7e // indirect
-	golang.org/x/mod v0.21.0 // indirect
-	golang.org/x/net v0.33.0 // indirect
-	golang.org/x/oauth2 v0.21.0 // indirect
-	golang.org/x/sync v0.10.0 // indirect
-	golang.org/x/sys v0.28.0 // indirect
-	golang.org/x/term v0.27.0 // indirect
-	golang.org/x/text v0.21.0 // indirect
+	golang.org/x/crypto v0.35.0 // indirect
+	golang.org/x/exp v0.0.0-20250106191152-7588d65b2ba8 // indirect
+	golang.org/x/mod v0.22.0 // indirect
+	golang.org/x/net v0.34.0 // indirect
+	golang.org/x/oauth2 v0.24.0 // indirect
+	golang.org/x/sync v0.11.0 // indirect
+	golang.org/x/sys v0.30.0 // indirect
+	golang.org/x/term v0.29.0 // indirect
+	golang.org/x/text v0.22.0 // indirect
 	golang.org/x/time v0.5.0 // indirect
-	golang.org/x/tools v0.24.0 // indirect
+	golang.org/x/tools v0.29.0 // indirect
 	google.golang.org/api v0.162.0 // indirect
 	google.golang.org/genproto v0.0.0-20240227224415-6ceb2ff114de // indirect
 	google.golang.org/genproto/googleapis/api v0.0.0-20240604185151-ef581f913117 // indirect
 	google.golang.org/genproto/googleapis/rpc v0.0.0-20240903143218-8af14fe29dc1 // indirect
 	google.golang.org/grpc v1.66.0 // indirect
-	google.golang.org/protobuf v1.34.2 // indirect
+	google.golang.org/protobuf v1.36.4 // indirect
 	gopkg.in/ini.v1 v1.67.0 // indirect
 	gopkg.in/natefinch/npipe.v2 v2.0.0-20160621034901-c1b8fa8bdcce // indirect
 	gopkg.in/yaml.v3 v3.0.1 // indirect
@@ -230,5 +230,5 @@ replace (
 	github.com/docker/docker => github.com/docker/docker v24.0.1+incompatible
 	github.com/gogo/protobuf => github.com/regen-network/protobuf v1.3.3-alpha.regen.1
 	github.com/syndtr/goleveldb => github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7
-	github.com/tendermint/tendermint => github.com/celestiaorg/celestia-core v1.47.0-tm-v0.34.35
+	github.com/tendermint/tendermint => github.com/celestiaorg/celestia-core v1.49.1-tm-v0.34.35
 )
```

### test/interchain/go.sum
```diff
@@ -204,6 +204,8 @@ github.com/ChainSafe/go-schnorrkel v1.0.0/go.mod h1:dpzHYVxLZcp8pjlV+O+UR8K0Hp/z
 github.com/ChainSafe/go-schnorrkel v1.1.0 h1:rZ6EU+CZFCjB4sHUE1jIu8VDoB/wRKZxoe1tkcO71Wk=
 github.com/ChainSafe/go-schnorrkel v1.1.0/go.mod h1:ABkENxiP+cvjFiByMIZ9LYbRoNNLeBLiakC1XeTFxfE=
 github.com/DataDog/datadog-go v3.2.0+incompatible/go.mod h1:LButxg5PwREeZtORoXG3tL4fMGNddJ+vMq1mwgfaqoQ=
+github.com/DataDog/zstd v1.5.6 h1:LbEglqepa/ipmmQJUDnSsfvA8e8IStVcGaFWDuxvGOY=
+github.com/DataDog/zstd v1.5.6/go.mod h1:g4AWEaM3yOg3HYfnJ3YIawPnVdXJh9QME85blwSAmyw=
 github.com/Microsoft/go-winio v0.6.1 h1:9/kr64B9VUZrLm5YYwbGtUJnMgqWVOdUAXu6Migciow=
 github.com/Microsoft/go-winio v0.6.1/go.mod h1:LRdKpFKfdobln8UmuiYcKPot9D2v6svN5+sAH+4kjUM=
 github.com/OneOfOne/xxhash v1.2.2 h1:KMrpdQIwFcEqXDklaen+P1axHaj9BSKzvpUUfnHldSE=
@@ -247,8 +249,8 @@ github.com/btcsuite/btcd/chaincfg/chainhash v1.0.1 h1:q0rUy8C/TYNBQS1+CGKw68tLOF
 github.com/btcsuite/btcd/chaincfg/chainhash v1.0.1/go.mod h1:7SFka0XMvUgj3hfZtydOrQY2mwhPclbT2snogU7SQQc=
 github.com/btcsuite/btcutil v1.0.3-0.20201208143702-a53e38424cce h1:YtWJF7RHm2pYCvA5t0RPmAaLUhREsKuKd+SLhxFbFeQ=
 github.com/btcsuite/btcutil v1.0.3-0.20201208143702-a53e38424cce/go.mod h1:0DVlHczLPewLcPGEIeUEzfOJhqGPQ0mJJRDBtD307+o=
-github.com/celestiaorg/celestia-core v1.47.0-tm-v0.34.35 h1:K0kSVRlKfsPwfiA4o8GNUNPfZ+wF1MnYajom4CzJxpQ=
-github.com/celestiaorg/celestia-core v1.47.0-tm-v0.34.35/go.mod h1:FSd32MUffdVUYIXW+m/1v5pHptRQF2RJC88fwsgrKG8=
+github.com/celestiaorg/celestia-core v1.49.1-tm-v0.34.35 h1:Fgm7Wj+378S0ktzpWiuIpjJTTfQYk3CNXKwvjHYLHeg=
+github.com/celestiaorg/celestia-core v1.49.1-tm-v0.34.35/go.mod h1:SI38xqZZ4ccoAxszUJqsJ/a5rOkzQRijzHQQlLKkyUc=
 github.com/celestiaorg/cosmos-sdk v1.27.0-sdk-v0.46.16 h1:qxWiGrDEcg4FzVTpIXU/v3wjP7q1Lz4AMhSBBRABInU=
 github.com/celestiaorg/cosmos-sdk v1.27.0-sdk-v0.46.16/go.mod h1:W30mNt3+2l516HVR8Gt9+Gf4qOrWC9/x18MTEx2GljE=
 github.com/celestiaorg/ibc-go/v6 v6.2.3 h1:INxacgOrRbPLPQVzbGA4QMDdcSLic6Ff5tf3fye3w/E=
@@ -292,10 +294,22 @@ github.com/cncf/xds/go v0.0.0-20240423153145-555b57ec207b h1:ga8SEFjZ60pxLcmhnTh
 github.com/cncf/xds/go v0.0.0-20240423153145-555b57ec207b/go.mod h1:W+zGtBO5Y1IgJhy4+A9GOqVhqLpfZi+vwmdNXUehLA8=
 github.com/cockroachdb/apd/v2 v2.0.2 h1:weh8u7Cneje73dDh+2tEVLUvyBc89iwepWCD8b8034E=
 github.com/cockroachdb/apd/v2 v2.0.2/go.mod h1:DDxRlzC2lo3/vSlmSoS7JkqbbrARPuFOGr0B9pvN3Gw=
+github.com/cockroachdb/errors v1.11.3 h1:5bA+k2Y6r+oz/6Z/RFlNeVCesGARKuC6YymtcDrbC/I=
+github.com/cockroachdb/errors v1.11.3/go.mod h1:m4UIW4CDjx+R5cybPsNrRbreomiFqt8o1h1wUVazSd8=
+github.com/cockroachdb/fifo v0.0.0-20240816210425-c5d0cb0b6fc0 h1:pU88SPhIFid6/k0egdR5V6eALQYq2qbSmukrkgIh/0A=
+github.com/cockroachdb/fifo v0.0.0-20240816210425-c5d0cb0b6fc0/go.mod h1:9/y3cnZ5GKakj/H4y9r9GTjCvAFta7KLgSHPJJYc52M=
+github.com/cockroachdb/logtags v0.0.0-20241215232642-bb51bb14a506 h1:ASDL+UJcILMqgNeV5jiqR4j+sTuvQNHdf2chuKj1M5k=
+github.com/cockroachdb/logtags v0.0.0-20241215232642-bb51bb14a506/go.mod h1:Mw7HqKr2kdtu6aYGn3tPmAftiP3QPX63LdK/zcariIo=
+github.com/cockroachdb/pebble v1.1.4 h1:5II1uEP4MyHLDnsrbv/EZ36arcb9Mxg3n+owhZ3GrG8=
+github.com/cockroachdb/pebble v1.1.4/go.mod h1:4exszw1r40423ZsmkG/09AFEG83I0uDgfujJdbL6kYU=
+github.com/cockroachdb/redact v1.1.5 h1:u1PMllDkdFfPWaNGMyLD1+so+aq3uUItthCFqzwPJ30=
+github.com/cockroachdb/redact v1.1.5/go.mod h1:BVNblN9mBWFyMyqK1k3AAiSxhvhfK2oOZZ2lK+dpvRg=
+github.com/cockroachdb/tokenbucket v0.0.0-20230807174530-cc333fc44b06 h1:zuQyyAKVxetITBuuhv3BI9cMrmStnpT18zmgmTxunpo=
+github.com/cockroachdb/tokenbucket v0.0.0-20230807174530-cc333fc44b06/go.mod h1:7nc4anLGjupUW/PeY5qiNYsdNXj7zopG+eqsS7To5IQ=
 github.com/coinbase/rosetta-sdk-go v0.7.9 h1:lqllBjMnazTjIqYrOGv8h8jxjg9+hJazIGZr9ZvoCcA=
 github.com/coinbase/rosetta-sdk-go v0.7.9/go.mod h1:0/knutI7XGVqXmmH4OQD8OckFrbQ8yMsUZTG7FXCR2M=
-github.com/cometbft/cometbft-db v0.7.0 h1:uBjbrBx4QzU0zOEnU8KxoDl18dMNgDh+zZRUE0ucsbo=
-github.com/cometbft/cometbft-db v0.7.0/go.mod h1:yiKJIm2WKrt6x8Cyxtq9YTEcIMPcEe4XPxhgX59Fzf0=
+github.com/cometbft/cometbft-db v1.0.3 h1:r14sw/ALiiT70btJ8dl1w5eWhPUOe6ZjMflUyuOJrPw=
+github.com/cometbft/cometbft-db v1.0.3/go.mod h1:mt5LIFwMQwioKxJ8+eZPyMscmAc7lbSoNMmW+xP1hvo=
 github.com/confio/ics23/go v0.9.1 h1:3MV46eeWwO3xCauKyAtuAdJYMyPnnchW4iLr2bTw6/U=
 github.com/confio/ics23/go v0.9.1/go.mod h1:4LPZ2NYqnYIVRklaozjNR1FScgDJ2s5Xrp+e/mYVRak=
 github.com/coreos/etcd v3.3.10+incompatible/go.mod h1:uF7uidLiAD3TWHmW31ZFd/JWoc32PjwdhPthX9715RE=
@@ -339,11 +353,16 @@ github.com/decred/dcrd/dcrec/secp256k1/v4 v4.1.0 h1:HbphB4TFFXpv7MNrT52FGrrgVXF1
 github.com/decred/dcrd/dcrec/secp256k1/v4 v4.1.0/go.mod h1:DZGJHZMqrU4JJqFAWUS2UO1+lbSKsdiOoYi9Zzey7Fc=
 github.com/desertbit/timer v0.0.0-20180107155436-c41aec40b27f h1:U5y3Y5UE0w7amNe7Z5G/twsBW0KEalRQXZzf8ufSh9I=
 github.com/desertbit/timer v0.0.0-20180107155436-c41aec40b27f/go.mod h1:xH/i4TFMt8koVQZ6WFms69WAsDWr2XsYL3Hkl7jkoLE=
+github.com/dgraph-io/badger v1.6.2 h1:mNw0qs90GVgGGWylh0umH5iag1j6n/PeJtNvL6KY/x8=
 github.com/dgraph-io/badger/v2 v2.2007.4 h1:TRWBQg8UrlUhaFdco01nO2uXwzKS7zd+HVdwV/GHc4o=
 github.com/dgraph-io/badger/v2 v2.2007.4/go.mod h1:vSw/ax2qojzbN6eXHIx6KPKtCSHJN/Uz0X0VPruTIhk=
+github.com/dgraph-io/badger/v4 v4.5.1 h1:7DCIXrQjo1LKmM96YD+hLVJ2EEsyyoWxJfpdd56HLps=
+github.com/dgraph-io/badger/v4 v4.5.1/go.mod h1:qn3Be0j3TfV4kPbVoK0arXCD1/nr1ftth6sbL5jxdoA=
 github.com/dgraph-io/ristretto v0.0.3-0.20200630154024-f66de99634de/go.mod h1:KPxhHT9ZxKefz+PCeOGsrHpl1qZ7i70dGTu2u+Ahh6E=
 github.com/dgraph-io/ristretto v0.1.1 h1:6CWw5tJNgpegArSHpNHJKldNeq03FQCwYvfMVWajOK8=
 github.com/dgraph-io/ristretto v0.1.1/go.mod h1:S1GPSBCYCIhmVNfcth17y2zZtQT6wzkzgwUve0VDWWA=
+github.com/dgraph-io/ristretto/v2 v2.1.0 h1:59LjpOJLNDULHh8MC4UaegN52lC4JnO2dITsie/Pa8I=
+github.com/dgraph-io/ristretto/v2 v2.1.0/go.mod h1:uejeqfYXpUomfse0+lO+13ATz4TypQYLJZzBSAemuB4=
 github.com/dgryski/go-farm v0.0.0-20190423205320-6a90982ecee2/go.mod h1:SqUrOPUnsFjfmXRMNPybcSiG0BgUW2AuFH8PAnS2iTw=
 github.com/dgryski/go-farm v0.0.0-20200201041132-a6ae2369ad13 h1:fAjc9m62+UWV/WAFKLNi6ZS0675eEUC9y3AlwSbQu1Y=
 github.com/dgryski/go-farm v0.0.0-20200201041132-a6ae2369ad13/go.mod h1:SqUrOPUnsFjfmXRMNPybcSiG0BgUW2AuFH8PAnS2iTw=
@@ -391,6 +410,8 @@ github.com/fsnotify/fsnotify v1.4.7/go.mod h1:jwhsz4b93w/PPRr/qN1Yymfu8t87LnFCMo
 github.com/fsnotify/fsnotify v1.4.9/go.mod h1:znqG4EE+3YCdAaPaxE2ZRY/06pZUdp0tY4IgpuI1SZQ=
 github.com/fsnotify/fsnotify v1.7.0 h1:8JEhPFa5W2WU7YfeZzPNqzMP6Lwt7L2715Ggo0nosvA=
 github.com/fsnotify/fsnotify v1.7.0/go.mod h1:40Bi/Hjc2AVfZrqy+aj+yEI+/bRxZnMJyTJwOpGvigM=
+github.com/getsentry/sentry-go v0.31.1 h1:ELVc0h7gwyhnXHDouXkhqTFSO5oslsRDk0++eyE0KJ4=
+github.com/getsentry/sentry-go v0.31.1/go.mod h1:CYNcMMz73YigoHljQRG+qPF+eMq8gG72XcGN/p71BAY=
 github.com/ghodss/yaml v1.0.0/go.mod h1:4dBDuWmgqj2HViK6kFavaiC9ZROes6MMH2rRYeMEF04=
 github.com/go-gl/glfw v0.0.0-20190409004039-e6da0acd62b1/go.mod h1:vR7hzQXu2zJy9AVAgeJqvqgH9Q5CA+iKCZ2gyEVpxRU=
 github.com/go-gl/glfw/v3.3/glfw v0.0.0-20191125211704-12ad95a8df72/go.mod h1:tQ2UAYgL5IevRw8kRxooKSPJfGvJ9fJQFa0TUsXzTg8=
@@ -424,8 +445,9 @@ github.com/golang/glog v1.2.4/go.mod h1:6AhwSGph0fcJtXVM/PEHPqZlFeoLxhs7/t5UDAwm
 github.com/golang/groupcache v0.0.0-20190702054246-869f871628b6/go.mod h1:cIg4eruTrX1D+g88fzRXU5OdNfaM+9IcxsU14FzY7Hc=
 github.com/golang/groupcache v0.0.0-20191227052852-215e87163ea7/go.mod h1:cIg4eruTrX1D+g88fzRXU5OdNfaM+9IcxsU14FzY7Hc=
 github.com/golang/groupcache v0.0.0-20200121045136-8c9f03a8e57e/go.mod h1:cIg4eruTrX1D+g88fzRXU5OdNfaM+9IcxsU14FzY7Hc=
-github.com/golang/groupcache v0.0.0-20210331224755-41bb18bfe9da h1:oI5xCqsCo564l8iNU+DwB5epxmsaqB+rhGL0m5jtYqE=
 github.com/golang/groupcache v0.0.0-20210331224755-41bb18bfe9da/go.mod h1:cIg4eruTrX1D+g88fzRXU5OdNfaM+9IcxsU14FzY7Hc=
+github.com/golang/groupcache v0.0.0-20241129210726-2c02b8208cf8 h1:f+oWsMOmNPc8JmEHVZIycC7hBoQxHH9pNKQORJNozsQ=
+github.com/golang/groupcache v0.0.0-20241129210726-2c02b8208cf8/go.mod h1:wcDNUvekVysuuOpQKo3191zZyTpiI6se1N1ULghS0sw=
 github.com/golang/mock v1.1.1/go.mod h1:oTYuIxOrZwtPieC+H1uAHpcLFnEyAGVDL/k47Jfbm0A=
 github.com/golang/mock v1.2.0/go.mod h1:oTYuIxOrZwtPieC+H1uAHpcLFnEyAGVDL/k47Jfbm0A=
 github.com/golang/mock v1.3.1/go.mod h1:sBzyDLLjw3U8JLTeZvSv8jJB+tU5PVekmnlKIyFUx0Y=
@@ -462,8 +484,10 @@ github.com/golang/snappy v0.0.5-0.20220116011046-fa5810519dcb h1:PBC98N2aIaM3XXi
 github.com/golang/snappy v0.0.5-0.20220116011046-fa5810519dcb/go.mod h1:/XxbfmMg8lxefKM7IXC3fBNl/7bRcc72aCRzEWrmP2Q=
 github.com/google/btree v0.0.0-20180813153112-4030bb1f1f0c/go.mod h1:lNA+9X1NB3Zf8V7Ke586lFgjr2dZNuvo3lPJSGZ5JPQ=
 github.com/google/btree v1.0.0/go.mod h1:lNA+9X1NB3Zf8V7Ke586lFgjr2dZNuvo3lPJSGZ5JPQ=
-github.com/google/btree v1.1.2 h1:xf4v41cLI2Z6FxbKm+8Bu+m8ifhj15JuZ9sa0jZCMUU=
-github.com/google/btree v1.1.2/go.mod h1:qOPhT0dTNdNzV6Z/lhRX0YXUafgPLFUh+gZMl761Gm4=
+github.com/google/btree v1.1.3 h1:CVpQJjYgC4VbzxeGVHfvZrv1ctoYCAI8vbl07Fcxlyg=
+github.com/google/btree v1.1.3/go.mod h1:qOPhT0dTNdNzV6Z/lhRX0YXUafgPLFUh+gZMl761Gm4=
+github.com/google/flatbuffers v25.1.24+incompatible h1:4wPqL3K7GzBd1CwyhSd3usxLKOaJN/AC6puCca6Jm7o=
+github.com/google/flatbuffers v25.1.24+incompatible/go.mod h1:1AeVuKshWv4vARoZatz6mlQ0JxURH0Kv5+zNeJKJCa8=
 github.com/google/go-cmp v0.2.0/go.mod h1:oXzfMopK8JAjlY9xF4vHSVASa0yLyX7SntLO5aqRK0M=
 github.com/google/go-cmp v0.3.0/go.mod h1:8QqcDgzrUqlUb/G2PQTWiueGozuR1884gddMywk6iLU=
 github.com/google/go-cmp v0.3.1/go.mod h1:8QqcDgzrUqlUb/G2PQTWiueGozuR1884gddMywk6iLU=
@@ -613,8 +637,8 @@ github.com/kisielk/errcheck v1.5.0/go.mod h1:pFxgyoBC7bSaBwPgfKdkLd5X25qrDl4LWUI
 github.com/kisielk/gotool v1.0.0/go.mod h1:XhKaO+MFFWcvkIS/tQcRk01m1F5IRFswLeQ+oQHNcck=
 github.com/klauspost/compress v1.12.3/go.mod h1:8dP1Hq4DHOhN9w426knH3Rhby4rFm6D8eO+e+Dq5Gzg=
 github.com/klauspost/compress v1.15.11/go.mod h1:QPwzmACJjUTFsnSHH934V6woptycfrDDJnH7hvFVbGM=
-github.com/klauspost/compress v1.17.9 h1:6KIumPrER1LHsvBVuDa0r5xaG0Es51mhhB9BQB2qeMA=
-github.com/klauspost/compress v1.17.9/go.mod h1:Di0epgTjJY877eYKx5yC51cX2A2Vl2ibi7bDH9ttBbw=
+github.com/klauspost/compress v1.17.11 h1:In6xLpyWOi1+C7tXUUWv2ot1QvBjxevKAaI6IXrJmUc=
+github.com/klauspost/compress v1.17.11/go.mod h1:pMDklpSncoRMuLFrf1W9Ss9KT+0rH90U12bZKk7uwG0=
 github.com/klauspost/cpuid/v2 v2.0.9/go.mod h1:FInQzS24/EEf25PyTYn52gqo7WaD8xa0213Md/qVLRg=
 github.com/klauspost/cpuid/v2 v2.2.6 h1:ndNyv040zDGIDh8thGkXYjnFtiN02M1PVVF+JE/48xc=
 github.com/klauspost/cpuid/v2 v2.2.6/go.mod h1:Lcz8mBdAVJIBVzewtcLocK12l3Y+JytZYpaMropDUws=
@@ -633,6 +657,8 @@ github.com/libp2p/go-buffer-pool v0.1.0 h1:oK4mSFcQz7cTQIfqbe4MIj9gLW+mnanjyFtc6
 github.com/libp2p/go-buffer-pool v0.1.0/go.mod h1:N+vh8gMqimBzdKkSMVuydVDq+UV5QTWy5HSiZacSbPg=
 github.com/libp2p/go-libp2p v0.27.8 h1:IX5x/4yKwyPQeVS2AXHZ3J4YATM9oHBGH1gBc23jBAI=
 github.com/libp2p/go-libp2p v0.27.8/go.mod h1:eCFFtd0s5i/EVKR7+5Ki8bM7qwkNW3TPTTSSW9sz8NE=
+github.com/linxGnu/grocksdb v1.9.8 h1:vOIKv9/+HKiqJAElJIEYv3ZLcihRxyP7Suu/Mu8Dxjs=
+github.com/linxGnu/grocksdb v1.9.8/go.mod h1:C3CNe9UYc9hlEM2pC82AqiGS3LRW537u9LFV4wIZuHk=
 github.com/magiconair/properties v1.8.0/go.mod h1:PppfXfuXeibc/6YijjN8zIbojt8czPbwD3XqdrwzmxQ=
 github.com/magiconair/properties v1.8.7 h1:IeQXZAiQcpL9mgcAe1Nu6cX9LLw6ExEHKjN0VQdvPDY=
 github.com/magiconair/properties v1.8.7/go.mod h1:Dhd985XPs7jluiymwWYZ0G4Z61jb3vdS329zhj2hYo0=
@@ -731,8 +757,8 @@ github.com/pmezard/go-difflib v1.0.1-0.20181226105442-5d4384ee4fb2/go.mod h1:iKH
 github.com/prometheus/client_golang v0.9.1/go.mod h1:7SWBe2y4D6OKWSNQJUaRYU/AaXPKyh/dDVn+NZz0KFw=
 github.com/prometheus/client_golang v1.0.0/go.mod h1:db9x61etRT2tGnBNRi70OPL5FsnadC4Ky3P0J6CfImo=
 github.com/prometheus/client_golang v1.4.0/go.mod h1:e9GMxYsXl05ICDXkRhurwBS4Q3OK1iX/F2sw+iXX5zU=
-github.com/prometheus/client_golang v1.20.3 h1:oPksm4K8B+Vt35tUhw6GbSNSgVlVSBH0qELP/7u83l4=
-github.com/prometheus/client_golang v1.20.3/go.mod h1:PIEt8X02hGcP8JWbeHyeZ53Y/jReSnHgO035n//V5WE=
+github.com/prometheus/client_golang v1.20.5 h1:cxppBPuYhUnsO6yo/aoRol4L7q7UFfdm+bR9r+8l63Y=
+github.com/prometheus/client_golang v1.20.5/go.mod h1:PIEt8X02hGcP8JWbeHyeZ53Y/jReSnHgO035n//V5WE=
 github.com/prometheus/client_model v0.0.0-20180712105110-5c3871d89910/go.mod h1:MbSGuTsp3dbXC40dX6PRTWyKYBIrTGTE9sqQNg2J8bo=
 github.com/prometheus/client_model v0.0.0-20190129233127-fd36f4220a90/go.mod h1:xMI15A0UPsDsEKsMN9yxemIoYk6Tm2C1GtYGdfGttqA=
 github.com/prometheus/client_model v0.0.0-20190812154241-14fe0d1b01d4/go.mod h1:xMI15A0UPsDsEKsMN9yxemIoYk6Tm2C1GtYGdfGttqA=
@@ -741,8 +767,8 @@ github.com/prometheus/client_model v0.6.1 h1:ZKSh/rekM+n3CeS952MLRAdFwIKqeY8b62p
 github.com/prometheus/client_model v0.6.1/go.mod h1:OrxVMOVHjw3lKMa8+x6HeMGkHMQyHDk9E3jmP2AmGiY=
 github.com/prometheus/common v0.4.1/go.mod h1:TNfzLD0ON7rHzMJeJkieUDPYmFC7Snx/y86RQel1bk4=
 github.com/prometheus/common v0.9.1/go.mod h1:yhUN8i9wzaXS3w1O07YhxHEBxD+W35wd8bs7vj7HSQ4=
-github.com/prometheus/common v0.55.0 h1:KEi6DK7lXW/m7Ig5i47x0vRzuBsHuvJdi5ee6Y3G1dc=
-github.com/prometheus/common v0.55.0/go.mod h1:2SECS4xJG1kd8XF9IcM1gMX6510RAEL65zxzNImwdc8=
+github.com/prometheus/common v0.62.0 h1:xasJaQlnWAeyHdUBeGjXmutelfJHWMRr+Fg4QszZ2Io=
+github.com/prometheus/common v0.62.0/go.mod h1:vyBcEuLSvWos9B1+CyL7JZ2up+uFzXhkqml0W5zIY1I=
 github.com/prometheus/procfs v0.0.0-20181005140218-185b4288413d/go.mod h1:c3At6R/oaqEKCNdg8wHV1ftS6bRYblBhIjjI8uT2IGk=
 github.com/prometheus/procfs v0.0.2/go.mod h1:TjEm7ze935MbeOT/UhFTIMYKhuLP4wbCsTZCD3I8kEA=
 github.com/prometheus/procfs v0.0.8/go.mod h1:7Qr8sr6344vo1JqZ6HhLceV9o3AJ1Ff+GxbHq6oeK9A=
@@ -762,8 +788,8 @@ github.com/remyoudompheng/bigfft v0.0.0-20230129092748-24d4a6f8daec/go.mod h1:qq
 github.com/rogpeppe/fastuuid v0.0.0-20150106093220-6724a57986af/go.mod h1:XWv6SoW27p1b0cqNHllgS5HIMJraePCO15w5zCzIWYg=
 github.com/rogpeppe/fastuuid v1.2.0/go.mod h1:jVj6XXZzXRy/MSR5jhDC/2q6DgLz+nrA6LYCDYWNEvQ=
 github.com/rogpeppe/go-internal v1.3.0/go.mod h1:M8bDsm7K2OlrFYOpmOWEs/qY81heoFRclV5y23lUDJ4=
-github.com/rogpeppe/go-internal v1.10.0 h1:TMyTOH3F/DB16zRVcYyreMH6GnZZrwQVAoYjRBZyWFQ=
-github.com/rogpeppe/go-internal v1.10.0/go.mod h1:UQnix2H7Ngw/k4C5ijL5+65zddjncjaFoBhdsK/akog=
+github.com/rogpeppe/go-internal v1.13.1 h1:KvO1DLK/DRN07sQ1LQKScxyZJuNnedQ5/wKSR38lUII=
+github.com/rogpeppe/go-internal v1.13.1/go.mod h1:uMEvuHeurkdAXX61udpOXGD/AzZDWNMNyH2VO9fmH0o=
 github.com/rootulp/interchaintest/v6 v6.1.0 h1:UPxyjjIqPywZ2zN9fMLd6ooxQNjowUAK2uFKzYK5srI=
 github.com/rootulp/interchaintest/v6 v6.1.0/go.mod h1:0bCJa4v7x7vN6a/z99qpa4Mg5ENAjv3/01LTGlBQ1qc=
 github.com/rs/cors v1.8.3 h1:O+qNyWn7Z+F9M0ILBHgMVPuB1xTOucVd5gtaYyXBpRo=
@@ -828,8 +854,6 @@ github.com/subosito/gotenv v1.6.0 h1:9NlTDc1FTs4qu0DDq7AEtTPNw6SVm7uBMsUCUjABIf8
 github.com/subosito/gotenv v1.6.0/go.mod h1:Dk4QP5c2W3ibzajGcXpNraDfq2IrhjMIvMSWPKKo0FU=
 github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7 h1:epCh84lMvA70Z7CTTCmYQn2CKbY8j86K7/FAIr141uY=
 github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7/go.mod h1:q4W45IWZaF22tdD+VEXcAWRA037jwmWEB5VWYORlTpc=
-github.com/tecbot/gorocksdb v0.0.0-20191217155057-f0fad39f321c h1:g+WoO5jjkqGAzHWCjJB1zZfXPIAaDpzXIEJ0eS6B5Ok=
-github.com/tecbot/gorocksdb v0.0.0-20191217155057-f0fad39f321c/go.mod h1:ahpPrc7HpcfEWDQRZEmnXMzHY03mLDYMCxeDzy46i+8=
 github.com/tendermint/go-amino v0.16.0 h1:GyhmgQKvqF82e2oZeuMSp9JTN0N09emoSZlb2lyGa2E=
 github.com/tendermint/go-amino v0.16.0/go.mod h1:TQU0M1i/ImAo+tYpZi73AU3V/dKeCoMC9Sphe2ZwGME=
 github.com/tendermint/tm-db v0.6.7 h1:fE00Cbl0jayAoqlExN6oyQJ7fR/ZtoVOmvPJ//+shu8=
@@ -861,8 +885,8 @@ github.com/zondax/hid v0.9.2 h1:WCJFnEDMiqGF64nlZz28E9qLVZ0KSJ7xpc5DLEyma2U=
 github.com/zondax/hid v0.9.2/go.mod h1:l5wttcP0jwtdLjqjMMWFVEE7d1zO0jvSPA9OPZxWpEM=
 github.com/zondax/ledger-go v0.14.3 h1:wEpJt2CEcBJ428md/5MgSLsXLBos98sBOyxNmCjfUCw=
 github.com/zondax/ledger-go v0.14.3/go.mod h1:IKKaoxupuB43g4NxeQmbLXv7T9AlQyie1UpHb342ycI=
-go.etcd.io/bbolt v1.3.6 h1:/ecaJf0sk1l4l6V4awd65v2C3ILy7MSj+s/x1ADCIMU=
-go.etcd.io/bbolt v1.3.6/go.mod h1:qXsaaIqmgQH0T+OPdb99Bf+PKfBBQVAdyD6TY9G8XM4=
+go.etcd.io/bbolt v1.3.11 h1:yGEzV1wPz2yVCLsD8ZAiGHhHVlczyC9d1rP43/VCRJ0=
+go.etcd.io/bbolt v1.3.11/go.mod h1:dksAq7YMXoljX0xu6VF5DMZGbhYYoLUalEiSySYAS4I=
 go.opencensus.io v0.21.0/go.mod h1:mSImk1erAIZhrmZN+AvHh14ztQfjbGwt4TtuofqLduU=
 go.opencensus.io v0.22.0/go.mod h1:+kGneAE2xo2IficOXnaByMWTGM9T73dGwxeWcUqIpI8=
 go.opencensus.io v0.22.2/go.mod h1:yxeiOL68Rb0Xd1ddK5vPZ/oVn4vY4Ynel7k9FzqtOIw=
@@ -908,8 +932,8 @@ golang.org/x/crypto v0.0.0-20191206172530-e9b2fee46413/go.mod h1:LzIPMQfyMNhhGPh
 golang.org/x/crypto v0.0.0-20200622213623-75b288015ac9/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
 golang.org/x/crypto v0.0.0-20200728195943-123391ffb6de/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
 golang.org/x/crypto v0.0.0-20210921155107-089bfa567519/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
-golang.org/x/crypto v0.31.0 h1:ihbySMvVjLAeSH1IbfcRTkD/iNscyz8rGzjF/E5hV6U=
-golang.org/x/crypto v0.31.0/go.mod h1:kDsLvtWBEx7MV9tJOj9bnXsPbxwJQ6csT/x4KIN4Ssk=
+golang.org/x/crypto v0.35.0 h1:b15kiHdrGCHrP6LvwaQ3c03kgNhhiMgvlhxHQhmg2Xs=
+golang.org/x/crypto v0.35.0/go.mod h1:dy7dXNW32cAb/6/PRuTNsix8T+vJAqvuIy5Bli/x0YQ=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190306152737-a1d7652674e8/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190510132918-efd6b22b2522/go.mod h1:ZjyILWgesfNpC6sMxTJOJm9Kp84zZh5NQWvqDGG3Qr8=
@@ -920,8 +944,8 @@ golang.org/x/exp v0.0.0-20191227195350-da58074b4299/go.mod h1:2RIsYlXP63K8oxa1u0
 golang.org/x/exp v0.0.0-20200119233911-0405dc783f0a/go.mod h1:2RIsYlXP63K8oxa1u096TMicItID8zy7Y6sNkU49FU4=
 golang.org/x/exp v0.0.0-20200207192155-f17229e696bd/go.mod h1:J/WKrq2StrnmMY6+EHIKF9dgMWnmCNThgcyBT1FY9mM=
 golang.org/x/exp v0.0.0-20200224162631-6cc2880d07d6/go.mod h1:3jZMyOhIsHpP37uCMkUooju7aAi5cS1Q23tOzKc+0MU=
-golang.org/x/exp v0.0.0-20240904232852-e7e105dedf7e h1:I88y4caeGeuDQxgdoFPUq097j7kNfw6uvuiNxUBfcBk=
-golang.org/x/exp v0.0.0-20240904232852-e7e105dedf7e/go.mod h1:akd2r19cwCdwSwWeIdzYQGa/EZZyqcOdwWiwj5L5eKQ=
+golang.org/x/exp v0.0.0-20250106191152-7588d65b2ba8 h1:yqrTHse8TCMW1M1ZCP+VAR/l0kKxwaAIqN/il7x4voA=
+golang.org/x/exp v0.0.0-20250106191152-7588d65b2ba8/go.mod h1:tujkw807nyEEAamNbDrEGzRav+ilXA7PCRAd6xsmwiU=
 golang.org/x/image v0.0.0-20190227222117-0694c2d4d067/go.mod h1:kZ7UVZpmo3dzQBMxlp+ypCbDeSB+sBbTgSJuh5dn5js=
 golang.org/x/image v0.0.0-20190802002840-cff245a6509b/go.mod h1:FeLwcggjj3mMvU+oOTbSwawSJRM1uh48EjtB4UJZlP0=
 golang.org/x/lint v0.0.0-20181026193005-c67002cb31c3/go.mod h1:UVdnD1Gm6xHRNCYTkRU2/jEulfH38KcIWyp/GAMgvoE=
@@ -948,8 +972,8 @@ golang.org/x/mod v0.4.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.1/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.2/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.6.0-dev.0.20220419223038-86c51ed26bb4/go.mod h1:jJ57K6gSWd91VN4djpZkiMVwK6gcyfeH4XE8wZrZaV4=
-golang.org/x/mod v0.21.0 h1:vvrHzRwRfVKSiLrG+d4FMl/Qi4ukBCE6kZlTUkDYRT0=
-golang.org/x/mod v0.21.0/go.mod h1:6SkKJ3Xj0I0BrPOZoBy3bdMptDDU9oJrpohJ3eWZ1fY=
+golang.org/x/mod v0.22.0 h1:D4nJWe9zXqHOmWqj4VMOJhvzj7bEZg4wEYa759z1pH4=
+golang.org/x/mod v0.22.0/go.mod h1:6SkKJ3Xj0I0BrPOZoBy3bdMptDDU9oJrpohJ3eWZ1fY=
 golang.org/x/net v0.0.0-20180724234803-3673e40ba225/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180826012351-8a410e7b638d/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180906233101-161cd47e91fd/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
@@ -1003,8 +1027,8 @@ golang.org/x/net v0.0.0-20220722155237-a158d28d115b/go.mod h1:XRhObCWvk6IyKnWLug
 golang.org/x/net v0.0.0-20220909164309-bea034e7d591/go.mod h1:YDH+HFinaLZZlnHAfSS6ZXJJ9M9t4Dl22yv3iI2vPwk=
 golang.org/x/net v0.0.0-20221014081412-f15817d10f9b/go.mod h1:YDH+HFinaLZZlnHAfSS6ZXJJ9M9t4Dl22yv3iI2vPwk=
 golang.org/x/net v0.1.0/go.mod h1:Cx3nUiGt4eDBEyega/BKRp+/AlGL8hYe7U9odMt2Cco=
-golang.org/x/net v0.33.0 h1:74SYHlV8BIgHIFC/LrYkOGIwL19eTYXQ5wc6TBuO36I=
-golang.org/x/net v0.33.0/go.mod h1:HXLR5J+9DxmrqMwG9qjGCxZ+zKXxBru04zlTvWlWuN4=
+golang.org/x/net v0.34.0 h1:Mb7Mrk043xzHgnRM88suvJFwzVrRfHEHJEl5/71CKw0=
+golang.org/x/net v0.34.0/go.mod h1:di0qlW3YNM5oh6GqDGQr92MyTozJPmybPK4Ev/Gm31k=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
 golang.org/x/oauth2 v0.0.0-20190226205417-e64efc72b421/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
 golang.org/x/oauth2 v0.0.0-20190604053449-0f29369cfe45/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
@@ -1030,8 +1054,8 @@ golang.org/x/oauth2 v0.0.0-20220822191816-0ebed06d0094/go.mod h1:h4gKUeWbJ4rQPri
 golang.org/x/oauth2 v0.0.0-20220909003341-f21342109be1/go.mod h1:h4gKUeWbJ4rQPri7E0u6Gs4e9Ri2zaLxzw5DI5XGrYg=
 golang.org/x/oauth2 v0.0.0-20221014153046-6fdb5e3db783/go.mod h1:h4gKUeWbJ4rQPri7E0u6Gs4e9Ri2zaLxzw5DI5XGrYg=
 golang.org/x/oauth2 v0.1.0/go.mod h1:G9FE4dLTsbXUu90h/Pf85g4w1D+SSAgR+q46nJZ8M4A=
-golang.org/x/oauth2 v0.21.0 h1:tsimM75w1tF/uws5rbeHzIWxEqElMehnc+iW793zsZs=
-golang.org/x/oauth2 v0.21.0/go.mod h1:XYTD2NtWslqkgxebSiOHnXEap4TF09sJSc7H1sXbhtI=
+golang.org/x/oauth2 v0.24.0 h1:KTBBxWqUa0ykRPLtV69rRto9TLXcqYkeswu48x/gvNE=
+golang.org/x/oauth2 v0.24.0/go.mod h1:XYTD2NtWslqkgxebSiOHnXEap4TF09sJSc7H1sXbhtI=
 golang.org/x/sync v0.0.0-20180314180146-1d60e4601c6f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20181108010431-42b317875d0f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20181221193216-37e7f081c4d4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
@@ -1046,8 +1070,8 @@ golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.0.0-20220601150217-0de741cfad7f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20220722155255-886fb9371eb4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20220929204114-8fcdb60fdcc0/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
-golang.org/x/sync v0.10.0 h1:3NQrjDixjgGwUOCaF8w2+VYHv0Ve/vGYSbdkTa98gmQ=
-golang.org/x/sync v0.10.0/go.mod h1:Czt+wKu1gCyEFDUtn0jG5QVvpJ6rzVqr5aXyt9drQfk=
+golang.org/x/sync v0.11.0 h1:GGz8+XQP4FvTTrjZPzNKTMFtSXH80RAzG+5ghFPgK9w=
+golang.org/x/sync v0.11.0/go.mod h1:Czt+wKu1gCyEFDUtn0jG5QVvpJ6rzVqr5aXyt9drQfk=
 golang.org/x/sys v0.0.0-20180830151530-49385e6e1522/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180905080454-ebe1bf3edb33/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180909124046-d0be0721c37e/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -1087,7 +1111,6 @@ golang.org/x/sys v0.0.0-20200523222454-059865788121/go.mod h1:h1NjWce9XRLGQEsW7w
 golang.org/x/sys v0.0.0-20200803210538-64077c9b5642/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20200814200057-3d37ad5750ed/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20200905004654-be1d3432aa8f/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
-golang.org/x/sys v0.0.0-20200923182605-d9f96fdee20d/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20200930185726-fdedc70b468f/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20201119102817-f84b799fce68/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20201201145000-ef89a241ccb3/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
@@ -1132,13 +1155,13 @@ golang.org/x/sys v0.1.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.5.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.6.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.12.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/sys v0.28.0 h1:Fksou7UEQUWlKvIdsqzJmUmCX3cZuD2+P3XyyzwMhlA=
-golang.org/x/sys v0.28.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
+golang.org/x/sys v0.30.0 h1:QjkSwP/36a20jFYWkSue1YwXzLmsV5Gfq7Eiy72C1uc=
+golang.org/x/sys v0.30.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/term v0.1.0/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
-golang.org/x/term v0.27.0 h1:WP60Sv1nlK1T6SupCHbXzSaN0b9wUmsPoRS9b61A23Q=
-golang.org/x/term v0.27.0/go.mod h1:iMsnZpn0cago0GOrHO2+Y7u7JPn5AylBrcoWkElMTSM=
+golang.org/x/term v0.29.0 h1:L6pJp37ocefwRRtYPKSWOWzOtWSxVajvz2ldH/xi3iU=
+golang.org/x/term v0.29.0/go.mod h1:6bl4lRlvVuDgSf3179VpIxBF0o10JUpXWOnI7nErv7s=
 golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.1-0.20180807135948-17ff2d5776d2/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
@@ -1149,8 +1172,8 @@ golang.org/x/text v0.3.5/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
 golang.org/x/text v0.4.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
-golang.org/x/text v0.21.0 h1:zyQAAkrwaneQ066sspRyJaG9VNi/YJ1NfzcGB3hZ/qo=
-golang.org/x/text v0.21.0/go.mod h1:4IBbMaMmOPCJ8SecivzSH54+73PCFmPWxNTLm+vZkEQ=
+golang.org/x/text v0.22.0 h1:bofq7m3/HAFvbF51jz3Q9wLg3jkvSPuiZu/pD1XwgtM=
+golang.org/x/text v0.22.0/go.mod h1:YRoo4H8PVmsu+E3Ou7cqLVH8oXWIHVoX0jqUWALQhfY=
 golang.org/x/time v0.0.0-20181108054448-85acf8d2951c/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20190308202827-9d24e82272b4/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20191024005414-555d28b269f0/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
@@ -1210,8 +1233,8 @@ golang.org/x/tools v0.1.3/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
 golang.org/x/tools v0.1.4/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
 golang.org/x/tools v0.1.5/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
 golang.org/x/tools v0.1.12/go.mod h1:hNGJHUnrk76NpqgfD5Aqm5Crs+Hm0VOH/i9J2+nxYbc=
-golang.org/x/tools v0.24.0 h1:J1shsA93PJUEVaUSaay7UXAyE8aimq3GW0pjlolpa24=
-golang.org/x/tools v0.24.0/go.mod h1:YhNqVBIfWHdzvTLs0d8LCuMhkKUgSUKldakyV7W/WDQ=
+golang.org/x/tools v0.29.0 h1:Xx0h3TtM9rzQpQuR4dKLrdglAmCEN5Oi+P74JdhdzXE=
+golang.org/x/tools v0.29.0/go.mod h1:KMQVMRsVxU6nHCFXrBPhDB8XncLNLM0lIy/F14RP588=
 golang.org/x/xerrors v0.0.0-20190717185122-a985d3407aa7/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191011141410-1b5146add898/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191204190536-9bdfabe68543/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
@@ -1443,8 +1466,8 @@ google.golang.org/protobuf v1.26.0/go.mod h1:9q0QmTI4eRPtz6boOQmLYwt+qCgq0jsYwAQ
 google.golang.org/protobuf v1.27.1/go.mod h1:9q0QmTI4eRPtz6boOQmLYwt+qCgq0jsYwAQnmE0givc=
 google.golang.org/protobuf v1.28.0/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
 google.golang.org/protobuf v1.28.1/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
-google.golang.org/protobuf v1.34.2 h1:6xV6lTsCfpGD21XK49h7MhtcApnLqkfYgPcdHftf6hg=
-google.golang.org/protobuf v1.34.2/go.mod h1:qYOHts0dSfpeUzUFpOMr/WGzszTmLH+DiWniOlNbLDw=
+google.golang.org/protobuf v1.36.4 h1:6A3ZDJHn/eNqc1i+IdefRzy/9PokBTPvcqMySR7NNIM=
+google.golang.org/protobuf v1.36.4/go.mod h1:9fA7Ob0pmnwhb644+1+CVWFRbNajQ6iRojtC/QF5bRE=
 gopkg.in/alecthomas/kingpin.v2 v2.2.6/go.mod h1:FMv+mEhP44yOT+4EoQTLFTRgOQ1FBLkstjWtayDeSgw=
 gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
 gopkg.in/check.v1 v1.0.0-20180628173108-788fd7840127/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
```
